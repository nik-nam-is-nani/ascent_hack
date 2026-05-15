from typing import List, Dict, Any, Optional
from models.task import Task, TaskType, SubTask
from tools import get_task_by_id
from .llm_client import get_llm_client


TASK_ANALYZER_SYSTEM_PROMPT = """You are a Task Analysis Agent specialized in breaking down complex tasks into manageable components and estimating completion effort.

Your role:
1. Analyze task descriptions to understand requirements
2. Identify required skills and expertise needed
3. Determine if tasks should be split into subtasks
4. Estimate time to completion
5. Classify tasks by type (CODE, PRESENTATION, RESEARCH, REPORT, DOCUMENTATION, REVIEW, MEETING)

Provide detailed analysis with:
- Required skills for the task
- Recommended approach
- Estimated complexity (simple, moderate, complex)
- Whether splitting is recommended
- Risk factors to consider

Respond in JSON format with your analysis."""


def analyze_task(task: Task) -> Dict[str, Any]:
    """Analyze a single task"""
    client = get_llm_client()

    prompt = f"""Analyze this task and provide detailed breakdown:

Task ID: {task.id}
Title: {task.title}
Description: {task.description}
Type: {task.task_type}
Priority: {task.priority}
Current Status: {task.status}
Progress: {task.progress}%
Estimated Hours: {task.estimated_hours}
Tags: {', '.join(task.tags)}

Provide analysis in JSON format:
{{
    "required_skills": ["list of skills needed"],
    "approach": "recommended approach",
    "complexity": "simple/moderate/complex",
    "should_split": true/false,
    "subtasks": [
        {{"title": "subtask title", "description": "description", "estimated_hours": number}}
    ],
    "risk_factors": ["list of potential risks"],
    "estimated_completion_hours": number,
    "confidence": 0.0-1.0
}}"""

    result = client.generate_json(TASK_ANALYZER_SYSTEM_PROMPT, prompt)
    return result


def analyze_tasks_for_employee(employee_id: str) -> Dict[str, Any]:
    """Analyze all pending tasks for an employee"""
    from tools import get_pending_tasks_by_employee

    tasks = get_pending_tasks_by_employee(employee_id)

    if not tasks:
        return {
            "employee_id": employee_id,
            "total_tasks": 0,
            "analysis": [],
            "summary": "No pending tasks"
        }

    task_analyses = []
    total_estimated_hours = 0
    tasks_requiring_split = 0

    for task in tasks:
        analysis = analyze_task(task)
        task_analyses.append({
            "task_id": task.id,
            "title": task.title,
            "analysis": analysis
        })
        total_estimated_hours += analysis.get("estimated_completion_hours", task.estimated_hours)
        if analysis.get("should_split"):
            tasks_requiring_split += 1

    return {
        "employee_id": employee_id,
        "total_tasks": len(tasks),
        "total_estimated_hours": total_estimated_hours,
        "tasks_requiring_split": tasks_requiring_split,
        "task_analyses": task_analyses,
        "summary": f"Analyzed {len(tasks)} tasks, {total_estimated_hours:.1f} hours total, {tasks_requiring_split} recommended for splitting"
    }


def classify_task_type(title: str, description: str, tags: List[str]) -> str:
    """Classify a task into a type"""
    client = get_llm_client()

    prompt = f"""Classify this task into one of these types: CODE, PRESENTATION, RESEARCH, REPORT, DOCUMENTATION, REVIEW, MEETING

Title: {title}
Description: {description}
Tags: {', '.join(tags)}

Respond with ONLY the task type (one word)."""

    result = client.generate(TASK_ANALYZER_SYSTEM_PROMPT, prompt)
    return result.strip().upper()


def estimate_complexity(task: Task) -> str:
    """Estimate task complexity"""
    factors = []

    if task.estimated_hours > 8:
        factors.append("long duration")
    if len(task.tags) > 3:
        factors.append("multiple domains")
    if task.priority.value in ["critical", "high"]:
        factors.append("high priority")
    if task.task_type in [TaskType.CODE, TaskType.RESEARCH]:
        factors.append("technical work")

    if len(factors) >= 3:
        return "complex"
    elif len(factors) >= 1:
        return "moderate"
    return "simple"


def get_required_skills_for_task(task: Task) -> List[str]:
    """Extract required skills from task analysis"""
    analysis = analyze_task(task)
    return analysis.get("required_skills", [])


def should_split_task(task: Task) -> bool:
    """Determine if a task should be split into subtasks"""
    if task.estimated_hours > 4:
        return True
    if task.task_type == TaskType.PRESENTATION:
        return True
    if task.task_type == TaskType.REPORT:
        return True

    analysis = analyze_task(task)
    return analysis.get("should_split", False)


def create_subtasks(task: Task, subtask_data: List[Dict]) -> List[SubTask]:
    """Create subtasks for a task"""
    subtasks = []
    for i, st_data in enumerate(subtask_data):
        subtask = SubTask(
            id=f"{task.id}-SUB-{i+1:02d}",
            title=st_data.get("title", ""),
            description=st_data.get("description", ""),
            status="not_started"
        )
        subtasks.append(subtask)
    return subtasks