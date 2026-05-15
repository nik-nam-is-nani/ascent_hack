from typing import List, Dict, Any, Optional
from models.employee import Employee
from tools import (
    get_available_employees,
    get_employee_by_id,
    calculate_skill_match,
    is_employee_busy,
    check_employee_availability
)
from .llm_client import get_llm_client


AVAILABILITY_AGENT_SYSTEM_PROMPT = """You are an Availability and Skill Matching Agent responsible for matching tasks to the best available team members.

Your role:
1. Evaluate employee availability and workload
2. Match task requirements to employee skills
3. Calculate compatibility scores
4. Rank candidates by fit
5. Consider workload distribution across team

For each task-employee match, consider:
- Skill overlap (technical skills, domain knowledge)
- Current workload and capacity
- Schedule availability
- Experience level
- Priority fit (critical tasks need senior resources)

Respond in JSON format with ranked candidates."""


def evaluate_employee_capacity(employee_id: str) -> Dict[str, Any]:
    """Evaluate an employee's capacity to take on more work"""
    employee = get_employee_by_id(employee_id)
    if not employee:
        return {"error": "Employee not found"}

    is_busy = is_employee_busy(employee_id)
    has_capacity = check_employee_availability(employee_id, hours_needed=4)

    # Workload score interpretation
    workload_capacity = 100 - employee.workload_score

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "current_workload_score": employee.workload_score,
        "available_capacity": workload_capacity,
        "is_in_meeting": is_busy,
        "has_time_available": has_capacity,
        "workload_level": employee.workload.value,
        "recommended_tasks": min(3, max(1, workload_capacity // 30))
    }


def calculate_skill_overlap(employee: Employee, required_skills: List[str]) -> float:
    """Calculate skill overlap between employee and required skills"""
    if not required_skills:
        return 0.5  # Neutral if no skills specified

    employee_skills = {skill.skill.lower() for skill in employee.skills}
    matched = sum(1 for s in required_skills if s.lower() in employee_skills)

    # Also factor in proficiency
    if matched > 0:
        proficiency_sum = 0
        for skill in employee.skills:
            if skill.skill.lower() in [s.lower() for s in required_skills]:
                proficiency_sum += skill.proficiency
        avg_proficiency = proficiency_sum / matched

        # Combine match rate with proficiency
        match_rate = matched / len(required_skills)
        return (match_rate * 0.6) + (avg_proficiency * 0.4)

    return 0.0


def score_candidate(
    employee: Employee,
    required_skills: List[str],
    task_priority: str,
    task_complexity: str
) -> Dict[str, Any]:
    """Score a candidate for a task"""
    skill_score = calculate_skill_overlap(employee, required_skills)

    # Workload factor (less workload = higher score)
    workload_factor = 1 - (employee.workload_score / 100)
    if employee.workload.value == "critical":
        workload_factor *= 0.3
    elif employee.workload.value == "high":
        workload_factor *= 0.6

    # Availability factor
    availability_factor = 1.0 if employee.is_available else 0.0

    # Skill match weight based on task type
    if task_complexity == "complex":
        skill_weight = 0.6
    else:
        skill_weight = 0.5

    # Calculate final score
    final_score = (
        (skill_score * skill_weight) +
        (workload_factor * 0.3) +
        (availability_factor * 0.2)
    )

    # Adjust for priority (critical tasks need higher skill scores)
    if task_priority == "critical" and skill_score < 0.7:
        final_score *= 0.8

    return {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "role": employee.role,
        "skill_score": round(skill_score, 3),
        "workload_score": employee.workload_score,
        "workload_factor": round(workload_factor, 3),
        "availability_factor": availability_factor,
        "final_score": round(final_score, 3),
        "is_available": employee.is_available,
        "skills": [s.skill for s in employee.skills]
    }


def find_best_matches(
    required_skills: List[str],
    task_priority: str,
    task_complexity: str,
    exclude_employee_ids: List[str] = [],
    threshold: float = 0.4
) -> List[Dict[str, Any]]:
    """Find the best matching employees for a task"""
    available_employees = get_available_employees()

    # Filter out excluded employees
    candidates = [
        emp for emp in available_employees
        if emp.id not in exclude_employee_ids
    ]

    if not candidates:
        return []

    # Score all candidates
    scored_candidates = []
    for emp in candidates:
        score_result = score_candidate(
            emp,
            required_skills,
            task_priority,
            task_complexity
        )
        scored_candidates.append(score_result)

    # Sort by final score
    scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)

    # Filter by threshold
    best_matches = [c for c in scored_candidates if c["final_score"] >= threshold]

    return best_matches


def get_team_availability_summary() -> Dict[str, Any]:
    """Get a summary of all team members' availability"""
    employees = get_available_employees()

    summary = {
        "total_employees": len(employees),
        "available": sum(1 for e in employees if e.is_available),
        "at_capacity": sum(1 for e in employees if e.workload_score >= 80),
        "available_for_new_tasks": [],
        "details": []
    }

    for emp in employees:
        capacity = evaluate_employee_capacity(emp.id)
        detail = {
            "id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "workload_score": emp.workload_score,
            "workload_level": emp.workload.value,
            "can_take_tasks": emp.workload_score < 75,
            "recommended_tasks": capacity.get("recommended_tasks", 0)
        }
        summary["details"].append(detail)

        if emp.workload_score < 75:
            summary["available_for_new_tasks"].append(emp.id)

    return summary


def recommend_task_distribution(
    tasks: List[Any],
    employees: List[Employee]
) -> Dict[str, Any]:
    """Recommend how to distribute tasks among available employees"""
    client = get_llm_client()

    # Prepare task and employee data
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            "id": task.id,
            "title": task.title,
            "priority": task.priority.value,
            "estimated_hours": task.estimated_hours
        })

    employees_data = []
    for emp in employees:
        employees_data.append({
            "id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "workload_score": emp.workload_score,
            "skills": [s.skill for s in emp.skills]
        })

    prompt = f"""Given these tasks and available employees, recommend optimal distribution:

Tasks: {json.dumps(tasks_data)}
Employees: {json.dumps(employees_data)}

Provide distribution in JSON format:
{{
    "distributions": [
        {{"task_id": "TASK-001", "recommended_employee_id": "EMP-002", "reason": "..."}}
    ],
    "unassigned_tasks": ["TASK-xxx"],
    "reasoning": "..."
}}

Respond ONLY with valid JSON."""

    result = client.generate_json(AVAILABILITY_AGENT_SYSTEM_PROMPT, prompt)
    return result


import json