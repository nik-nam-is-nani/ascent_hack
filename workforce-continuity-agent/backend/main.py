import os
import json
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
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
    reset_tasks_for_employee,
    update_employee
)
from database import initialize_database
from agents import run_orchestrator, reset_absence
from agents.activity import get_activity_feed, set_broadcast_callback, broadcast_activity, activity_tracker

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
    try:
        employees, tasks = initialize_database()
        print(f"Database initialized with {len(employees)} employees and {len(tasks)} tasks")
        broadcast_activity("system", "System initialized", {"employees": len(employees), "tasks": len(tasks)})
    except Exception as e:
        print(f"Startup error: {e}")


from database.simulation_seeder import seed_ecommerce_project

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Workforce Continuity Agent",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/simulation/start")
async def start_simulation(data: Optional[Dict[str, str]] = Body(None)):
    """Start a full project simulation"""
    try:
        employees, tasks = seed_ecommerce_project()
        github_token = (data.get("github_token") if data else None) or os.getenv("GITHUB_TOKEN")
        github_repo_url = (data.get("github_repo_url") if data else None) or os.getenv("GITHUB_REPO_URL")
        
        # Trigger P1's absence automatically to start the pipeline
        # Alice Chen is now Riya Sharma (P1)
        asyncio.create_task(run_orchestrator("P1", github_token, github_repo_url))
        
        return {
            "status": "simulation_started",
            "employees": len(employees),
            "tasks": len(tasks),
            "target": "Riya Sharma (P1 - Homepage)"
        }
    except Exception as e:
        print(f"Simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from tools.workspace_tool import get_workspace_files, clone_repository

@app.post("/api/workspace/clone")
async def clone_repo(data: Dict[str, str]):
    """Clone a real repository into the workspace"""
    repo_url = data.get("url")
    token = data.get("github_token")
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL required")
    
    broadcast_activity("phase_2", f"Cloning repository: {repo_url}...", {"url": repo_url})
    
    # workspace_tool.clone_repository now returns (success, message)
    success, message = clone_repository(repo_url, token)
    if success:
        return {"status": "success", "message": f"Cloned {repo_url} successfully"}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to clone: {message}")

@app.get("/api/workspace/files")
async def list_workspace_files():
    """Get all files in the simulated workspace"""
    return {"files": get_workspace_files()}

@app.get("/api/workspace/status")
async def workspace_status():
    """Get git repository status of the workspace"""
    from tools.github_tool import get_repo_status
    return get_repo_status()

@app.get("/api/workspace/file/{file_path:path}")
async def get_workspace_file_content(file_path: str):
    """Get content of a specific file in the workspace"""
    from tools.workspace_tool import WORKSPACE_ROOT
    full_path = os.path.join(WORKSPACE_ROOT, file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(full_path, "r", encoding="utf-8") as f:
        return {"content": f.read()}


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
async def mark_absence(employee_id: str, data: Optional[Dict[str, Any]] = Body(None)):
    """Mark an employee as absent and trigger the agent pipeline"""
    try:
        print(f"[API] ===== Triggering pipeline for employee: {employee_id} =====", flush=True)
        employee = get_employee_by_id(employee_id)
        if not employee:
            print(f"Employee {employee_id} not found")
            raise HTTPException(status_code=404, detail="Employee not found")

        # Get token from body or env
        github_token = None
        github_repo_url = None
        if data and isinstance(data, dict):
            github_token = data.get("github_token")
            github_repo_url = data.get("github_repo_url")
        
        if not github_token:
             github_token = os.getenv("GITHUB_TOKEN")
        if not github_repo_url:
            github_repo_url = os.getenv("GITHUB_REPO_URL")

        # Run the orchestrator asynchronously in the background
        print(f"[API] Token: {github_token[:20] if github_token else 'NONE'}...", flush=True)
        print(f"[API] Repo: {github_repo_url}", flush=True)

        async def run_pipeline():
            try:
                result = await run_orchestrator(employee_id, github_token, github_repo_url)
                print(f"[API] Pipeline result: {result.get('status', 'unknown')}", flush=True)
            except Exception as e:
                import traceback
                print(f"[API] Pipeline FAILED: {e}", flush=True)
                traceback.print_exc()

        asyncio.create_task(run_pipeline())

        return {
            "status": "processing",
            "employee_id": employee_id,
            "message": f"Agent pipeline triggered for {employee.name}",
            "background_task": True,
            "repo_sync": bool(github_repo_url)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"CRITICAL ERROR in mark_absence: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to trigger: {str(e)}")


@app.post("/api/absence/{employee_id}/reset")
async def reset_absence_endpoint(employee_id: str):
    """Reset an employee's absence status"""
    result = reset_absence(employee_id)
    return result


# Webhook endpoint for external systems (HR systems, calendars, etc.)
@app.post("/webhook/absence")
async def webhook_absence(data: Dict[str, Any]):
    """
    Webhook endpoint for external HR systems or calendars to trigger absence handling.
    Expected payload: {"employee_id": "EMP-001", "reason": "sick", "source": "calendar"}
    """
    employee_id = data.get("employee_id")
    reason = data.get("reason", "unspecified")
    source = data.get("source", "webhook")

    if not employee_id:
        raise HTTPException(status_code=400, detail="employee_id is required")

    employee = get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")

    # Get optional GitHub credentials from environment or data
    github_token = data.get("github_token") or os.getenv("GITHUB_TOKEN")
    github_repo_url = data.get("github_repo_url") or os.getenv("GITHUB_REPO_URL")

    # Log the webhook trigger
    broadcast_activity("webhook", f"Absence triggered via {source}: {reason}", {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "reason": reason,
        "source": source
    })

    # Trigger the same pipeline as /api/absence/{employee_id}
    async def run_pipeline():
        try:
            result = await run_orchestrator(employee_id, github_token, github_repo_url)
            print(f"[WEBHOOK] Pipeline result: {result.get('status', 'unknown')}", flush=True)
        except Exception as e:
            import traceback
            print(f"[WEBHOOK] Pipeline FAILED: {e}", flush=True)
            traceback.print_exc()

    asyncio.create_task(run_pipeline())

    return {
        "status": "accepted",
        "employee_id": employee_id,
        "employee_name": employee.name,
        "reason": reason,
        "source": source,
        "message": f"Absence webhook received for {employee.name}, pipeline triggered"
    }


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
    from agents import reallocate_all_tasks

    tasks = get_pending_tasks_by_employee(employee_id)
    decisions = reallocate_all_tasks(employee_id)

    report = generate_manager_report(employee, tasks, decisions)

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "report": report
    }


# PDF report endpoints
@app.get("/api/reports")
async def list_reports():
    """List all generated PDF reports"""
    import os
    import glob
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    pdf_files = glob.glob(os.path.join(data_dir, "report_*.pdf"))
    reports = []
    for pdf_path in sorted(pdf_files, reverse=True):
        filename = os.path.basename(pdf_path)
        reports.append({
            "filename": filename,
            "path": pdf_path,
            "download_url": f"/api/reports/{filename}",
            "size_kb": round(os.path.getsize(pdf_path) / 1024, 1)
        })
    return {"reports": reports}


@app.get("/api/reports/{filename}")
async def download_report(filename: str):
    """Download or view a PDF report"""
    import os
    from fastapi.responses import FileResponse
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    pdf_path = os.path.join(data_dir, filename)
    if not os.path.exists(pdf_path) or not filename.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)


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
