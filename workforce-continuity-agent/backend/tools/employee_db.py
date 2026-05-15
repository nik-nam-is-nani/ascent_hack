from typing import List, Optional, Dict
from datetime import datetime
import json
import os
from models.employee import Employee, SkillTag, WorkloadLevel

# In-memory database
employees_db: Dict[str, Employee] = {}


def get_all_employees() -> List[Employee]:
    return list(employees_db.values())


def get_employee_by_id(employee_id: str) -> Optional[Employee]:
    return employees_db.get(employee_id)


def get_available_employees() -> List[Employee]:
    return [e for e in employees_db.values() if e.is_available and not e.is_absent]


def update_employee(employee: Employee) -> Employee:
    employees_db[employee.id] = employee
    return employee


def mark_employee_absent(employee_id: str) -> Employee:
    employee = employees_db.get(employee_id)
    if employee:
        employee.is_absent = True
        employee.is_available = False
    return employee


def get_employee_skills(employee_id: str) -> List[str]:
    employee = employees_db.get(employee_id)
    if employee:
        return [skill.skill for skill in employee.skills]
    return []


def get_employees_by_department(department: str) -> List[Employee]:
    return [e for e in employees_db.values() if e.department == department]


def calculate_skill_match(employee_id: str, required_skills: List[str]) -> float:
    employee = employees_db.get(employee_id)
    if not employee:
        return 0.0

    if not required_skills:
        return 0.5

    employee_skill_set = {skill.skill.lower() for skill in employee.skills}
    matched_skills = sum(1 for s in required_skills if s.lower() in employee_skill_set)

    return matched_skills / len(required_skills) if required_skills else 0.0


def load_employees(employees: List[Employee]) -> None:
    for emp in employees:
        employees_db[emp.id] = emp


def reset_employee_status(employee_id: str) -> Employee:
    employee = employees_db.get(employee_id)
    if employee:
        employee.is_absent = False
        employee.is_available = True
    return employee