import os
import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import asyncio

from models.employee import Employee
from models.task import Task
from tools import (
    get_all_employees,
    get_employee_by_id,
    get_all_tasks,
    get_task_by_id,
    get_pending_tasks_by_employee,
    update_task,
    reset_employee_status,
    reset_tasks_for_employee
)
from database import initialize_database
from agents import (
    run_orchestrator,
    reset_absence,
    get_activity_feed,
    set_broadcast_callback,
    broadcast_activity
)

# Initialize FastAPI app
app = FastAPI(
    title="Workforce Continuity Agent",
    description="Multi-agent autonomous system for handling employee absences",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass  # Remove dead connections


manager = ConnectionManager()


# Set up broadcast callback for agent activities
async def broadcast_to_clients(activity: Dict[str, Any]):
    """Broadcast agent activity to all WebSocket clients"""
    await manager.broadcast(activity)


set_broadcast_callback(broadcast_to_clients)


# Event lifespan - initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    employees, tasks = initialize_database()
    print(f"Database initialized with {len(employees)} employees and {len(tasks)} tasks")
    broadcast_activity("system", "System initialized", {"employees": len(employees), "tasks": len(tasks)})


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Workforce Continuity Agent",
        "version": "1.0.0",
        "status": "running"
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Employee endpoints
@app.get("/api/employees")
async def list_employees():
    """Get all employees"""
    employees = get_all_employees()
    return {
        "employees": [emp.model_dump() for emp in employees],
        "total": len(employees)
    }


@app.get("/api/employees/{employee_id}")
async def get_employee(employee_id: str):
    """Get a specific employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee.model_dump()


@app.get("/api/employees/{employee_id}/tasks")
async def get_employee_tasks(employee_id: str):
    """Get tasks assigned to an employee"""
    tasks = get_pending_tasks_by_employee(employee_id)
    return {
        "employee_id": employee_id,
        "tasks": [task.model_dump() for task in tasks],
        "total": len(tasks)
    }


# Task endpoints
@app.get("/api/tasks")
async def list_tasks():
    """Get all tasks"""
    tasks = get_all_tasks()
    return {
        "tasks": [task.model_dump() for task in tasks],
        "total": len(tasks)
    }


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get a specific task"""
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()


@app.put("/api/tasks/{task_id}")
async def update_task_endpoint(task_id: str, task_data: Dict[str, Any]):
    """Update a task"""
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task fields
    for key, value in task_data.items():
        if hasattr(task, key):
            setattr(task, key, value)

    updated_task = update_task(task)
    return updated_task.model_dump()


# Main action endpoints
@app.post("/api/absence/{employee_id}")
async def mark_absence(employee_id: str):
    """Mark an employee as absent and trigger the agent pipeline"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if employee.is_absent:
        raise HTTPException(status_code=400, detail="Employee is already marked as absent")

    # Run the orchestrator
    result = await run_orchestrator(employee_id)

    return {
        "status": "success",
        "message": f"Agent pipeline completed for {employee.name}",
        "result": result
    }


@app.post("/api/absence/{employee_id}/reset")
async def reset_absence_endpoint(employee_id: str):
    """Reset an employee's absence status"""
    result = reset_absence(employee_id)
    return result


# WebSocket endpoint for real-time updates
@app.websocket("/ws/activity")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time agent activity feed"""
    await manager.connect(websocket)

    # Send initial activity feed
    activities = get_activity_feed()
    await websocket.send_json({
        "type": "initial",
        "activities": activities
    })

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "reset":
                    # Reset activity feed
                    activities = get_activity_feed()
                    await websocket.send_json({
                        "type": "reset",
                        "activities": activities
                    })

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Activity feed endpoint
@app.get("/api/activity")
async def get_activity():
    """Get current activity feed"""
    return {
        "activities": get_activity_feed(),
        "total": len(get_activity_feed())
    }


@app.post("/api/activity/clear")
async def clear_activity():
    """Clear activity feed"""
    from agents.orchestrator import activity_tracker
    activity_tracker.clear()
    return {"status": "cleared"}


# Manager report endpoint
@app.get("/api/report/{employee_id}")
async def get_report(employee_id: str):
    """Get manager report for an absent employee"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    from agents.orchestrator import generate_manager_report
    from tools import get_pending_tasks_by_employee
    from agents import get_reallocation_report

    tasks = get_pending_tasks_by_employee(employee_id)
    decisions = get_reallocation_report({"employee_id": employee_id}, employee_id).get("decisions", [])

    # Convert decisions back to Decision objects
    from models.task import Decision
    from datetime import datetime
    decision_objects = [
        Decision(
            task_id=d["task_id"],
            decision_type=d["decision"],
            assigned_to=d.get("assigned_to"),
            confidence=float(d.get("confidence", "0%").replace("%", "")) / 100,
            reasoning=d.get("reasoning", ""),
            alternative_options=[],
            timestamp=datetime.now()
        )
        for d in decisions
    ]

    report = generate_manager_report(employee, tasks, decision_objects)

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "report": report
    }


# Dashboard stats endpoint
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    employees = get_all_employees()
    tasks = get_all_tasks()

    absent_count = sum(1 for e in employees if e.is_absent)
    available_count = sum(1 for e in employees if e.is_available and not e.is_absent)

    # Task status counts
    from models.task import TaskStatus
    task_status_counts = {}
    for status in TaskStatus:
        task_status_counts[status.value] = sum(1 for t in tasks if t.status == status)

    return {
        "employees": {
            "total": len(employees),
            "absent": absent_count,
            "available": available_count,
            "at_work": len(employees) - absent_count
        },
        "tasks": {
            "total": len(tasks),
            "by_status": task_status_counts
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)