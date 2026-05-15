import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from models.employee import Employee
from models.task import Task, Decision, TaskManifest, TaskStatus
from tools import (
    get_employee_by_id,
    get_pending_tasks_by_employee,
    update_task,
    mark_employee_absent,
    reset_tasks_for_employee,
    reset_employee_status,
    notify_task_reassignment
)

from .task_analyzer import analyze_tasks_for_employee, analyze_task
from .reallocation_agent import reallocate_all_tasks, validate_reallocation, get_reallocation_report
from .executor_agent import execute_tasks_auto, get_executor_summary


class AgentActivity:
    """Track agent activity for real-time feed"""
    def __init__(self):
        self.activities: List[Dict[str, Any]] = []

    def add(self, phase: str, message: str, details: Dict = None):
        activity = {
            "id": len(self.activities) + 1,
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "message": message,
            "details": details or {}
        }
        self.activities.append(activity)
        return activity

    def get_all(self) -> List[Dict[str, Any]]:
        return self.activities

    def clear(self):
        self.activities = []


# Global activity tracker
activity_tracker = AgentActivity()


def get_activity_feed() -> List[Dict[str, Any]]:
    """Get all activities"""
    return activity_tracker.get_all()


# WebSocket broadcast callback
broadcast_callback: Optional[Callable] = None


def set_broadcast_callback(callback: Callable):
    """Set the WebSocket broadcast callback"""
    global broadcast_callback
    broadcast_callback = callback


def broadcast_activity(phase: str, message: str, details: Dict = None):
    """Broadcast activity to WebSocket clients"""
    activity = activity_tracker.add(phase, message, details)
    if broadcast_callback:
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(broadcast_callback(activity))
            else:
                loop.run_until_complete(broadcast_callback(activity))
        except Exception:
            pass  # Silently fail if broadcast fails
    return activity


async def run_orchestrator(employee_id: str) -> Dict[str, Any]:
    """Run the full 6-phase agent pipeline asynchronously with delays to simulate thinking"""

    # Get employee info
    employee = get_employee_by_id(employee_id)
    if not employee:
        return {"error": "Employee not found"}

    # Phase 1: Mark employee absent
    broadcast_activity(
        "phase_1",
        f"Detected absence: {employee.name} ({employee.role})",
        {"employee_id": employee_id, "employee_name": employee.name}
    )
    
    await asyncio.sleep(1.5) # Simulate detection time
    mark_employee_absent(employee_id)

    # Phase 2: Get pending tasks
    broadcast_activity(
        "phase_2",
        f"Retrieving {employee.name}'s profile and pending tasks...",
        {"employee_id": employee_id}
    )
    
    await asyncio.sleep(1.2)
    pending_tasks = get_pending_tasks_by_employee(employee_id)

    if not pending_tasks:
        broadcast_activity(
            "phase_2",
            f"No pending tasks for {employee.name}",
            {"task_count": 0}
        )
        return {
            "employee_id": employee_id,
            "employee_name": employee.name,
            "tasks_handled": 0,
            "message": "No pending tasks to handle"
        }

    broadcast_activity(
        "phase_2",
        f"Found {len(pending_tasks)} pending task(s) in system",
        {"task_count": len(pending_tasks), "tasks": [t.id for t in pending_tasks]}
    )
    
    await asyncio.sleep(1.0)

    # Phase 3: Analyze tasks
    broadcast_activity(
        "phase_3",
        "Phase 3: Deep analysis of task requirements and dependencies...",
        {"phase": "task_analysis"}
    )
    
    # Granular analysis steps
    analysis_thoughts = [
        "Scanning organizational task manifest for critical path dependencies...",
        "Evaluating historical performance metrics for available team members...",
        "Calculating complexity-to-skill ratio for pending deliverables...",
        "Synthesizing optimal reallocation strategy using Neural Engine V4..."
    ]
    for thought in analysis_thoughts:
        broadcast_activity(
            "phase_3",
            thought,
            {"sub_phase": "analysis_thought", "task_id": "GLOBAL"}
        )
        await asyncio.sleep(0.8)

    await asyncio.sleep(0.5)
    task_analysis = analyze_tasks_for_employee(employee_id)

    broadcast_activity(
        "phase_3",
        f"Analysis complete: {len(pending_tasks)} tasks — {task_analysis['total_estimated_hours']:.1f} hours total",
        task_analysis
    )
    
    await asyncio.sleep(1.0)

    # Phase 4: Reallocate tasks to humans
    broadcast_activity(
        "phase_4",
        "Phase 4: Optimization engine finding best matches for reassignment...",
        {"phase": "reallocation"}
    )
    
    planning_steps = [
        "Mapping task priorities to available team capacity...",
        "Validating skill-set alignment for target assignees...",
        "Optimizing workload balance across departments...",
        "Finalizing continuity decisions and routing notifications..."
    ]
    for step in planning_steps:
        broadcast_activity(
            "phase_4",
            step,
            {"sub_phase": "planning_step"}
        )
        await asyncio.sleep(0.7)

    await asyncio.sleep(1.0)
    decisions = reallocate_all_tasks(employee_id)

    # Notify assigned employees
    for decision in decisions:
        if decision.decision_type == "reassign" and decision.assigned_to:
            assigned_emp = get_employee_by_id(decision.assigned_to)
            if assigned_emp:
                notify_task_reassignment(
                    decision.assigned_to,
                    assigned_emp.name,
                    decision.task_id,
                    decision.task_id,
                    decision.reasoning
                )

                task = next((t for t in pending_tasks if t.id == decision.task_id), None)
                if task:
                    broadcast_activity(
                        "phase_4",
                        f"Allocated: Task {decision.task_id} assigned to {assigned_emp.name} (confidence: {decision.confidence:.0%})",
                        {"task_id": decision.task_id, "assigned_to": assigned_emp.name, "confidence": decision.confidence}
                    )
                    await asyncio.sleep(0.5) # Slight delay between assignments

    await asyncio.sleep(1.0)

    # Phase 5: Execute remaining tasks with AI
    auto_complete_tasks = [
        t for t in pending_tasks
        if any(d.task_id == t.id and d.decision_type == "auto_complete" for d in decisions)
    ]

    if auto_complete_tasks:
        broadcast_activity(
            "phase_5",
            f"Agent Executor starting autonomous completion of {len(auto_complete_tasks)} task(s)...",
            {"phase": "execution", "task_count": len(auto_complete_tasks)}
        )
        
        await asyncio.sleep(1.0)

        for task in auto_complete_tasks:
            # Related skills for this task type
            skills_map = {
                "CODE": ["Python", "FastAPI", "React", "System Architecture"],
                "RESEARCH": ["Data Synthesis", "Market Analysis", "Critical Review"],
                "REPORT": ["Data Visualization", "Executive Writing", "Strategic Planning"],
                "PRESENTATION": ["Visual Design", "Narrative Structure", "Public Speaking"],
                "DOCUMENTATION": ["Technical Writing", "API Design", "User Experience"]
            }
            
            task_type_str = str(task.task_type.value).upper()
            required_skills = skills_map.get(task_type_str, ["General Intelligence", "Problem Solving"])
            
            # Simulate skill learning for this task
            for skill in required_skills:
                broadcast_activity(
                    "phase_5",
                    f"Acquiring skill: {skill}...",
                    {"sub_phase": "learning", "skill": skill, "task_id": task.id}
                )
                await asyncio.sleep(0.8)
                
                broadcast_activity(
                    "phase_5",
                    f"Mastered skill: {skill}",
                    {"sub_phase": "mastered", "skill": skill, "task_id": task.id}
                )
                await asyncio.sleep(0.4)

            # Now implement the task using learned skills
            broadcast_activity(
                "phase_5",
                f"Implementing task {task.id}: {task.title}",
                {"sub_phase": "implementing", "task_id": task.id, "skills_used": required_skills}
            )
            
            await asyncio.sleep(1.0)

            # Detailed implementation steps
            implementation_steps = [
                {"action": "creating_files", "message": f"Creating new module: {task_type_str.lower()}_handler.py", "file": f"src/{task_type_str.lower()}_handler.py"},
                {"action": "updating_code", "message": f"Injecting logic into {task.id} core service...", "file": "src/services/core.py"},
                {"action": "editing_apis", "message": "Registering new FastAPI routes for task execution...", "route": f"/api/auto/{task.id}"},
                {"action": "writing_react", "message": "Generating UI components for task artifacts...", "component": f"{task_type_str.capitalize()}Viewer.jsx"}
            ]

            for step in implementation_steps:
                broadcast_activity(
                    "phase_5",
                    f"Action: {step['message']}",
                    {
                        "sub_phase": "execution_step", 
                        "task_id": task.id, 
                        "action": step['action'],
                        "details": step,
                        "code_preview": _generate_mock_code(step['action'], task)
                    }
                )
                await asyncio.sleep(1.2)
            
            # Actual execution call
            result = execute_tasks_auto([task])[0]
            
            status = result.get("status", "unknown")
            if status == "completed":
                broadcast_activity(
                    "phase_5",
                    f"Successfully applied skills to complete task {task.id}",
                    {"sub_phase": "applied", "task_id": task.id, "executed_by": "AgentExecutor", "artifacts": result.get("artifacts", [])}
                )
            else:
                broadcast_activity(
                    "phase_5",
                    f"Execution failed on task {task.id}: {result.get('error', 'Unknown error')}",
                    {"task_id": task.id, "status": "failed"}
                )
            await asyncio.sleep(1.0) # Delay between task executions

    await asyncio.sleep(1.0)

    # Phase 6: Generate manager report
    broadcast_activity(
        "phase_6",
        "Phase 6: Compiling final continuity report for management...",
        {"phase": "report_generation"}
    )
    
    await asyncio.sleep(2.0)

    # Generate final report
    reallocation_report = get_reallocation_report(decisions, employee_id)

    # Create manifest
    manifest = TaskManifest(
        tasks=pending_tasks,
        decisions=decisions,
        generated_at=datetime.now(),
        absent_employee_id=employee_id
    )

    # Generate markdown report
    report = generate_manager_report(employee, pending_tasks, decisions)

    broadcast_activity(
        "phase_6",
        f"Continuity pipeline completed. {len(pending_tasks)} tasks handled efficiently.",
        {
            "total_tasks": len(pending_tasks),
            "reassigned": reallocation_report.get("reassigned_count", 0),
            "auto_completed": reallocation_report.get("auto_complete_count", 0)
        }
    )

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "employee_role": employee.role,
        "total_tasks": len(pending_tasks),
        "reassigned": sum(1 for d in decisions if d.decision_type == "reassign"),
        "auto_completed": sum(1 for d in decisions if d.decision_type == "auto_complete"),
        "manifest": manifest.model_dump(),
        "report": report,
        "reallocation_report": reallocation_report,
        "timestamp": datetime.now().isoformat()
    }


def generate_manager_report(
    employee: Employee,
    tasks: List[Task],
    decisions: List[Decision]
) -> str:
    """Generate a markdown manager report"""

    report_lines = [
        f"# Workforce Continuity Agent — Manager Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"## Absent Employee",
        "",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Name | {employee.name} |",
        f"| Role | {employee.role} |",
        f"| Department | {employee.department} |",
        f"| Email | {employee.email} |",
        "",
        "## Task Summary",
        "",
        f"- **Total Tasks Handled:** {len(tasks)}",
        f"- **Reassigned to Team:** {sum(1 for d in decisions if d.decision_type == 'reassign')}",
        f"- **Auto-Completed by Agent:** {sum(1 for d in decisions if d.decision_type == 'auto_complete')}",
        "",
        "## Task Details",
        "",
        "| Task ID | Title | Decision | Assigned To | Confidence |",
        "|---------|-------|----------|-------------|------------|",
    ]

    for task in tasks:
        decision = next((d for d in decisions if d.task_id == task.id), None)
        if decision:
            assigned = decision.assigned_to or "Agent Executor"
            report_lines.append(f"| {task.id} | {task.title} | {decision.decision_type} | {assigned} | {decision.confidence:.0%} |")

    report_lines.append("")

    # Add decision reasoning section
    report_lines.extend([
        "## Decision Rationale",
        ""
    ])

    for decision in decisions:
        task = next((t for t in tasks if t.id == decision.task_id), None)
        report_lines.append(f"### {decision.task_id}: {task.title if task else ''}")
        report_lines.append("")
        report_lines.append(f"- **Decision:** {decision.decision_type}")
        if decision.assigned_to:
            emp = get_employee_by_id(decision.assigned_to)
            report_lines.append(f"- **Assigned To:** {emp.name if emp else decision.assigned_to}")
        report_lines.append(f"- **Confidence:** {decision.confidence:.0%}")
        report_lines.append(f"- **Reasoning:** {decision.reasoning}")
        if decision.alternative_options:
            report_lines.append(f"- **Alternatives Considered:** {', '.join(decision.alternative_options)}")
        report_lines.append("")

    # Add recommendations
    report_lines.extend([
        "## Recommendations",
        "",
        "1. Monitor reassigned tasks to ensure smooth handover",
        "2. Review auto-completed artifacts for quality assurance",
        "3. Consider cross-training to reduce single-point dependencies",
        "4. Schedule follow-up with absent employee upon return",
        ""
    ])

    return "\n".join(report_lines)


def reset_absence(employee_id: str) -> Dict[str, Any]:
    """Reset an employee's absence status and restore tasks"""
    employee = get_employee_by_id(employee_id)

    if not employee:
        return {"error": "Employee not found"}

    # Reset employee status
    reset_employee_status(employee_id)

    # Reset tasks to original assignee
    reset_tasks_for_employee(employee_id)

    broadcast_activity(
        "reset",
        f"Reset {employee.name}'s status - tasks restored to original assignee",
        {"employee_id": employee_id}
    )

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "status": "reset",
        "message": f"Employee status reset and tasks restored to {employee.name}"
    }


def _generate_mock_code(action: str, task: Task) -> str:
    """Generate fake code for visualization"""
    if action == "creating_files":
        return f"import os\n\ndef init_handler():\n    print('Initializing {task.id}')\n    return True"
    elif action == "updating_code":
        return f"def process_task(task_id):\n    # Auto-implementation for {task.id}\n    result = run_logic()\n    return result"
    elif action == "editing_apis":
        return f"@app.get('/api/auto/{task.id}')\nasync def handle_task():\n    return {{'status': 'completed', 'task': '{task.title}'}}"
    elif action == "writing_react":
        return f"export const {task.id}Viewer = () => {{\n  return <div>Viewing {task.title}</div>\n}}"
    return "# Processing..."
