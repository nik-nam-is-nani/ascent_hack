from typing import List, Optional, Dict
from datetime import datetime
import json
import os
import sqlite3
from models.task import Task, TaskStatus, TaskPriority, TaskType, SubTask

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "workforce.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row

# Create tables if not exist
conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        assigned_to TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Migration: add columns if they don't exist (for existing databases)
try:
    conn.execute("SELECT assigned_to FROM tasks LIMIT 1")
except sqlite3.OperationalError:
    conn.execute("ALTER TABLE tasks ADD COLUMN assigned_to TEXT")
    conn.execute("ALTER TABLE tasks ADD COLUMN status TEXT")
    conn.commit()
    # Backfill from JSON data
    for row in conn.execute("SELECT id, data FROM tasks"):
        try:
            d = json.loads(row["data"])
            conn.execute("UPDATE tasks SET assigned_to = ?, status = ? WHERE id = ?",
                         (d.get("assigned_to"), d.get("status"), row["id"]))
        except Exception:
            pass
    conn.commit()


def _task_from_row(row) -> Optional[Task]:
    if not row:
        return None
    data = json.loads(row["data"])
    return Task(
        id=data["id"],
        title=data["title"],
        description=data["description"],
        task_type=TaskType(data["task_type"]),
        priority=TaskPriority(data["priority"]),
        status=TaskStatus(data["status"]),
        assigned_to=data["assigned_to"],
        original_assignee=data["original_assignee"],
        estimated_hours=data.get("estimated_hours"),
        progress=data.get("progress", 0),
        created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        tags=data.get("tags", []),
        subtasks=[SubTask(**st) for st in data.get("subtasks", [])],
        artifacts=data.get("artifacts", [])
    )


def _task_to_json(task: Task) -> str:
    return json.dumps({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type.value if task.task_type else "code",
        "priority": task.priority.value if task.priority else "medium",
        "status": task.status.value if task.status else "not_started",
        "assigned_to": task.assigned_to,
        "original_assignee": task.original_assignee,
        "estimated_hours": task.estimated_hours,
        "progress": task.progress,
        "created_at": task.created_at.isoformat() if task.created_at else datetime.now().isoformat(),
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "tags": task.tags,
        "subtasks": [{"id": st.id, "title": st.title, "status": st.status.value if st.status else "not_started"} for st in task.subtasks],
        "artifacts": task.artifacts
    })


def get_all_tasks() -> List[Task]:
    cursor = conn.execute("SELECT * FROM tasks")
    return [row for row in (_task_from_row(r) for r in cursor) if row]


def get_task_by_id(task_id: str) -> Optional[Task]:
    cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    return _task_from_row(row)


def get_tasks_by_employee(employee_id: str) -> List[Task]:
    cursor = conn.execute("SELECT * FROM tasks WHERE assigned_to = ?", (employee_id,))
    rows = cursor.fetchall()
    return [row for row in (_task_from_row(r) for r in rows) if row]


def get_pending_tasks_by_employee(employee_id: str) -> List[Task]:
    cursor = conn.execute(
        "SELECT * FROM tasks WHERE assigned_to = ? AND status IN (?, ?)",
        (employee_id, TaskStatus.NOT_STARTED.value, TaskStatus.IN_PROGRESS.value)
    )
    rows = cursor.fetchall()
    return [row for row in (_task_from_row(r) for r in rows) if row]


def update_task(task: Task) -> Task:
    json_data = _task_to_json(task)
    conn.execute(
        "INSERT OR REPLACE INTO tasks (id, data, assigned_to, status, updated_at) VALUES (?, ?, ?, ?, ?)",
        (task.id, json_data, task.assigned_to, task.status.value if task.status else "not_started", datetime.now().isoformat())
    )
    conn.commit()
    return task


def get_tasks_by_status(status: TaskStatus) -> List[Task]:
    cursor = conn.execute("SELECT * FROM tasks WHERE status = ?", (status.value,))
    rows = cursor.fetchall()
    return [row for row in (_task_from_row(r) for r in rows) if row]


def load_tasks(tasks: List[Task]) -> None:
    for task in tasks:
        update_task(task)


def get_task_by_ids(task_ids: List[str]) -> List[Task]:
    placeholders = ",".join("?" * len(task_ids))
    cursor = conn.execute(f"SELECT * FROM tasks WHERE id IN ({placeholders})", task_ids)
    rows = cursor.fetchall()
    return [row for row in (_task_from_row(r) for r in rows) if row]


def add_subtask(task_id: str, subtask: SubTask) -> Task:
    task = get_task_by_id(task_id)
    if task:
        task.subtasks.append(subtask)
        update_task(task)
    return task


def update_subtask_status(task_id: str, subtask_id: str, status: TaskStatus) -> Task:
    task = get_task_by_id(task_id)
    if task:
        for st in task.subtasks:
            if st.id == subtask_id:
                st.status = status
        update_task(task)
    return task


def add_artifact(task_id: str, artifact: str) -> Task:
    task = get_task_by_id(task_id)
    if task:
        task.artifacts.append(artifact)
        update_task(task)
    return task


def reset_tasks_for_employee(employee_id: str) -> None:
    cursor = conn.execute("SELECT * FROM tasks WHERE assigned_to = ?", (employee_id,))
    rows = cursor.fetchall()
    for row in rows:
        task = _task_from_row(row)
        if task:
            task.assigned_to = task.original_assignee
            task.status = TaskStatus.NOT_STARTED
            task.progress = 0
            update_task(task)
