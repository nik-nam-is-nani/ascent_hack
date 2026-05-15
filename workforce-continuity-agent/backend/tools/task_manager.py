from typing import List, Optional, Dict
from datetime import datetime
from models.task import Task, TaskStatus, SubTask

# In-memory database
tasks_db: Dict[str, Task] = {}


def get_all_tasks() -> List[Task]:
    return list(tasks_db.values())


def get_task_by_id(task_id: str) -> Optional[Task]:
    return tasks_db.get(task_id)


def get_tasks_by_employee(employee_id: str) -> List[Task]:
    return [t for t in tasks_db.values() if t.assigned_to == employee_id]


def get_pending_tasks_by_employee(employee_id: str) -> List[Task]:
    return [
        t for t in tasks_db.values()
        if t.assigned_to == employee_id
        and t.status in [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS]
    ]


def update_task(task: Task) -> Task:
    tasks_db[task.id] = task
    return task


def get_tasks_by_status(status: TaskStatus) -> List[Task]:
    return [t for t in tasks_db.values() if t.status == status]


def load_tasks(tasks: List[Task]) -> None:
    for task in tasks:
        tasks_db[task.id] = task


def get_task_by_ids(task_ids: List[str]) -> List[Task]:
    return [tasks_db[tid] for tid in task_ids if tid in tasks_db]


def add_subtask(task_id: str, subtask: SubTask) -> Task:
    task = tasks_db.get(task_id)
    if task:
        task.subtasks.append(subtask)
    return task


def update_subtask_status(task_id: str, subtask_id: str, status: TaskStatus) -> Task:
    task = tasks_db.get(task_id)
    if task:
        for st in task.subtasks:
            if st.id == subtask_id:
                st.status = status
    return task


def add_artifact(task_id: str, artifact: str) -> Task:
    task = tasks_db.get(task_id)
    if task:
        task.artifacts.append(artifact)
    return task


def reset_tasks_for_employee(employee_id: str) -> None:
    for task in tasks_db.values():
        if task.assigned_to == employee_id:
            task.assigned_to = task.original_assignee
            task.status = TaskStatus.NOT_STARTED
            task.progress = 0