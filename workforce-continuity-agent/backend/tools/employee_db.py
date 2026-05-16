from typing import List, Optional, Dict
from datetime import datetime
import json
import os
import sqlite3
from models.employee import Employee, SkillTag, WorkloadLevel

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "workforce.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row

# Create tables if not exist
conn.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        is_available INTEGER DEFAULT 1,
        is_absent INTEGER DEFAULT 0,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

# Migration: add columns if they don't exist (for existing databases)
for col, col_type, default in [
    ("is_available", "INTEGER", "1"),
    ("is_absent", "INTEGER", "0"),
    ("department", "TEXT", "NULL")
]:
    try:
        conn.execute(f"SELECT {col} FROM employees LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute(f"ALTER TABLE employees ADD COLUMN {col} {col_type} DEFAULT {default}")
        conn.commit()
        # Backfill from JSON data
        for row in conn.execute("SELECT id, data FROM employees"):
            try:
                d = json.loads(row["data"])
                val = d.get(col)
                if col in ("is_available", "is_absent"):
                    val = 1 if val else 0
                conn.execute(f"UPDATE employees SET {col} = ? WHERE id = ?", (val, row["id"]))
            except Exception:
                pass
        conn.commit()


def _employee_from_row(row) -> Optional[Employee]:
    if not row:
        return None
    data = json.loads(row["data"])
    skills = [SkillTag(skill=s["skill"], proficiency=s["proficiency"]) for s in data.get("skills", [])]
    return Employee(
        id=data["id"],
        name=data["name"],
        role=data["role"],
        department=data["department"],
        skills=skills,
        workload=WorkloadLevel(data["workload"]),
        workload_score=data["workload_score"],
        is_available=data["is_available"],
        is_absent=data["is_absent"],
        email=data["email"],
        avatar_color=data.get("avatar_color")
    )


def _employee_to_json(employee: Employee) -> str:
    return json.dumps({
        "id": employee.id,
        "name": employee.name,
        "role": employee.role,
        "department": employee.department,
        "skills": [{"skill": s.skill, "proficiency": s.proficiency} for s in employee.skills],
        "workload": employee.workload.value if employee.workload else "medium",
        "workload_score": employee.workload_score,
        "is_available": employee.is_available,
        "is_absent": employee.is_absent,
        "email": employee.email,
        "avatar_color": employee.avatar_color
    })


def get_all_employees() -> List[Employee]:
    cursor = conn.execute("SELECT * FROM employees")
    return [row for row in (_employee_from_row(r) for r in cursor) if row]


def get_employee_by_id(employee_id: str) -> Optional[Employee]:
    cursor = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    row = cursor.fetchone()
    return _employee_from_row(row)


def get_available_employees() -> List[Employee]:
    cursor = conn.execute("SELECT * FROM employees WHERE is_available = 1 AND is_absent = 0")
    rows = cursor.fetchall()
    return [row for row in (_employee_from_row(r) for r in rows) if row]


def update_employee(employee: Employee) -> Employee:
    json_data = _employee_to_json(employee)
    conn.execute(
        "INSERT OR REPLACE INTO employees (id, data, is_available, is_absent, department, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (employee.id, json_data, 1 if employee.is_available else 0, 1 if employee.is_absent else 0,
         employee.department, datetime.now().isoformat())
    )
    conn.commit()
    return employee


def mark_employee_absent(employee_id: str) -> Employee:
    employee = get_employee_by_id(employee_id)
    if employee:
        employee.is_absent = True
        employee.is_available = False
        update_employee(employee)
    return employee


def get_employee_skills(employee_id: str) -> List[str]:
    employee = get_employee_by_id(employee_id)
    if employee:
        return [skill.skill for skill in employee.skills]
    return []


def get_employees_by_department(department: str) -> List[Employee]:
    cursor = conn.execute("SELECT * FROM employees WHERE department = ?", (department,))
    rows = cursor.fetchall()
    return [row for row in (_employee_from_row(r) for r in rows) if row]


def calculate_skill_match(employee_id: str, required_skills: List[str]) -> float:
    employee = get_employee_by_id(employee_id)
    if not employee:
        return 0.0

    if not required_skills:
        return 0.5

    employee_skill_set = {skill.skill.lower() for skill in employee.skills}
    matched_skills = sum(1 for s in required_skills if s.lower() in employee_skill_set)

    return matched_skills / len(required_skills) if required_skills else 0.0


def load_employees(employees: List[Employee]) -> None:
    for emp in employees:
        update_employee(emp)


def reset_employee_status(employee_id: str) -> Employee:
    employee = get_employee_by_id(employee_id)
    if employee:
        employee.is_absent = False
        employee.is_available = True
        update_employee(employee)
    return employee


def is_database_empty() -> bool:
    """Check if the database has any employees"""
    cursor = conn.execute("SELECT COUNT(*) as count FROM employees")
    return cursor.fetchone()["count"] == 0
