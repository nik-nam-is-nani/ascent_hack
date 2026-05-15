from typing import List, Dict, Any, Optional
from datetime import datetime
from models.task import Task, TaskStatus, Decision
from tools import get_pending_tasks_by_employee, get_employee_by_id, update_task
from .availability_agent import find_best_matches, get_team_availability_summary
from .llm_client import get_llm_client


REALLOCATION_AGENT_SYSTEM_PROMPT = """You are a Task Reallocation Agent responsible for making intelligent decisions about task distribution when an employee is absent.

Your role:
1. Review task analysis and skill matching results
2. Decide whether to reassign, auto-complete, or split tasks
3. Provide clear reasoning for each decision
4. Consider dependencies and priorities
5. Balance workload across the team

Decisions should maximize:
- Task completion likelihood
- Team efficiency
- Quality of work

Respond in JSON format with clear decision logic."""


def make_reallocation_decision(
    task: Task,
    best_matches: List[Dict[str, Any]],
    threshold: float = 0.6
) -> Dict[str, Any]:
    """Make a decision about how to handle a task"""
    if not best_matches or best_matches[0]["final_score"] < threshold:
        # No suitable human match - use executor agent
        return {
            "decision": "auto_complete",
            "assigned_to": None,
            "reason": f"No human match above {threshold} threshold. Best score: {best_matches[0]['final_score'] if best_matches else 0:.2f}",
            "confidence": 0.8 if not best_matches else (1 - best_matches[0]["final_score"]),
            "alternative_options": []
        }

    best_candidate = best_matches[0]

    return {
        "decision": "reassign",
        "assigned_to": best_candidate["employee_id"],
        "assigned_to_name": best_candidate["employee_name"],
        "reason": f"Best skill match: {best_candidate['skill_score']:.0%}, workload: {best_candidate['workload_score']}%",
        "confidence": best_candidate["final_score"],
        "alternative_options": [
            {
                "employee_id": m["employee_id"],
                "employee_name": m["employee_name"],
                "score": m["final_score"]
            }
            for m in best_matches[1:3]
        ]
    }


def process_task_reallocation(
    task: Task,
    required_skills: List[str],
    threshold: float = 0.6
) -> Decision:
    """Process a single task for reallocation"""
    best_matches = find_best_matches(
        required_skills=required_skills,
        task_priority=task.priority.value,
        task_complexity="moderate",
        exclude_employee_ids=[task.assigned_to],
        threshold=0.3  # Lower threshold for initial matching
    )

    decision_data = make_reallocation_decision(task, best_matches, threshold)

    decision = Decision(
        task_id=task.id,
        decision_type=decision_data["decision"],
        assigned_to=decision_data.get("assigned_to"),
        confidence=decision_data["confidence"],
        reasoning=decision_data["reason"],
        alternative_options=[f"{opt['employee_name']} ({opt['score']:.0%})" for opt in decision_data.get("alternative_options", [])],
        timestamp=datetime.now()
    )

    return decision


def reallocate_all_tasks(employee_id: str) -> List[Decision]:
    """Reallocate all pending tasks for an absent employee"""
    from tools import task_manager

    pending_tasks = get_pending_tasks_by_employee(employee_id)

    if not pending_tasks:
        return []

    decisions = []

    for task in pending_tasks:
        # Get task analysis to find required skills
        from .task_analyzer import get_required_skills_for_task

        required_skills = get_required_skills_for_task(task)

        # Make reallocation decision
        decision = process_task_reallocation(task, required_skills)
        decisions.append(decision)

        # Update task with decision info
        task.decision_reason = decision.reasoning
        task.confidence_score = decision.confidence

        # Apply the decision
        if decision.decision_type == "reassign" and decision.assigned_to:
            task.assigned_to = decision.assigned_to
            task.status = TaskStatus.REASSIGNED

            # Update the employee in task manager
            update_task(task)
        elif decision.decision_type == "auto_complete":
            # Will be handled by executor agent
            pass

    return decisions


def validate_reallocation(decisions: List[Decision], employee_id: str) -> Dict[str, Any]:
    """Validate that reallocation decisions are balanced"""
    from tools import get_employee_by_id

    # Count tasks per employee
    task_counts = {}
    for decision in decisions:
        if decision.assigned_to:
            task_counts[decision.assigned_to] = task_counts.get(decision.assigned_to, 0) + 1

    # Get team availability summary
    team_summary = get_team_availability_summary()

    # Check for overloading
    overloaded = []
    for emp_id, count in task_counts.items():
        emp = get_employee_by_id(emp_id)
        if emp and emp.workload_score + (count * 10) > 90:
            overloaded.append({
                "employee_id": emp_id,
                "employee_name": emp.name,
                "current_workload": emp.workload_score,
                "new_tasks": count,
                "warning": "May become overloaded"
            })

    return {
        "total_tasks": len(decisions),
        "reassigned": sum(1 for d in decisions if d.decision_type == "reassign"),
        "auto_completed": sum(1 for d in decisions if d.decision_type == "auto_complete"),
        "task_distribution": task_counts,
        "potential_overloads": overloaded,
        "is_balanced": len(overloaded) == 0
    }


def optimize_reallocation(
    decisions: List[Decision],
    employee_id: str
) -> List[Decision]:
    """Optimize reallocation decisions to balance workload"""
    # Simple optimization: if any employee is overloaded, reassign some tasks
    validation = validate_reallocation(decisions, employee_id)

    if not validation["is_balanced"]:
        # Find less loaded alternatives
        from .availability_agent import get_team_availability_summary

        team_summary = get_team_availability_summary()
        available_employees = {
            d["id"]: d["recommended_tasks"]
            for d in team_summary["details"]
            if d["can_take_tasks"]
        }

        # Try to reassign from overloaded employees
        for overload in validation["potential_overloads"]:
            # Find tasks that could be moved
            for decision in decisions:
                if decision.assigned_to == overload["employee_id"]:
                    # Try to find a better match
                    pass  # Simplified for demo

    return decisions


def get_reallocation_report(decisions: List[Decision], employee_id: str) -> Dict[str, Any]:
    """Generate a report of reallocation decisions"""
    employee = get_employee_by_id(employee_id)

    report = {
        "absent_employee": employee.name if employee else "Unknown",
        "absent_employee_role": employee.role if employee else "Unknown",
        "total_tasks": len(decisions),
        "reassigned_count": sum(1 for d in decisions if d.decision_type == "reassign"),
        "auto_complete_count": sum(1 for d in decisions if d.decision_type == "auto_complete"),
        "decisions": [],
        "validation": validate_reallocation(decisions, employee_id)
    }

    for decision in decisions:
        task = task_manager.get_task_by_id(decision.task_id)
        report["decisions"].append({
            "task_id": decision.task_id,
            "task_title": task.title if task else "Unknown",
            "decision": decision.decision_type,
            "assigned_to": decision.assigned_to,
            "confidence": f"{decision.confidence:.0%}",
            "reasoning": decision.reasoning
        })

    return report