from datetime import datetime
from models.employee import Employee, SkillTag, WorkloadLevel
from models.task import Task, TaskPriority, TaskStatus, TaskType
from tools import employee_db, task_manager, calendar_tool

def seed_project_simulation():
    """Seed a realistic project simulation with multiple tasks and employees"""
    
    # 1. Clear existing data
    employee_db.employees = {}
    task_manager.tasks = []
    
    # 2. Add employees
    employees = [
        Employee(
            id="DEV-001", name="Alice Chen", role="Lead Backend", department="Core",
            skills=[SkillTag(skill="Python", proficiency=0.9), SkillTag(skill="FastAPI", proficiency=0.8)],
            workload=WorkloadLevel.HIGH, workload_score=80, is_available=True, is_absent=False,
            email="alice@ascent.ai", avatar_color="#6366f1"
        ),
        Employee(
            id="DEV-002", name="Bob Smith", role="Frontend Lead", department="UI/UX",
            skills=[SkillTag(skill="React", proficiency=0.9), SkillTag(skill="TypeScript", proficiency=0.8)],
            workload=WorkloadLevel.MEDIUM, workload_score=50, is_available=True, is_absent=False,
            email="bob@ascent.ai", avatar_color="#10b981"
        ),
        Employee(
            id="DEV-003", name="Charlie Day", role="DevOps Ninja", department="Infrastructure",
            skills=[SkillTag(skill="Docker", proficiency=0.9), SkillTag(skill="AWS", proficiency=0.8)],
            workload=WorkloadLevel.LOW, workload_score=20, is_available=True, is_absent=False,
            email="charlie@ascent.ai", avatar_color="#f59e0b"
        )
    ]
    employee_db.load_employees(employees)
    
    # 3. Add Project Tasks
    tasks = [
        # Alice's tasks (Absence will trigger these)
        Task(
            id="ARCH-001", title="Initialize Neural Core API", 
            description="Set up the main FastAPI structure with pydantic models for the neural engine.",
            task_type=TaskType.CODE, priority=TaskPriority.CRITICAL, status=TaskStatus.NOT_STARTED,
            assigned_to="DEV-001", original_assignee="DEV-001", estimated_hours=4, progress=0,
            created_at=datetime.now(), tags=["backend", "api"]
        ),
        Task(
            id="ARCH-002", title="Implement JWT Auth Provider", 
            description="Create the authentication layer for secure neural link connections.",
            task_type=TaskType.CODE, priority=TaskPriority.HIGH, status=TaskStatus.NOT_STARTED,
            assigned_to="DEV-001", original_assignee="DEV-001", estimated_hours=3, progress=0,
            created_at=datetime.now(), tags=["security", "auth"]
        ),
        # Bob's tasks (He is present)
        Task(
            id="UI-001", title="Build Realtime Dashboard", 
            description="Implement the React dashboard for monitoring agent activities.",
            task_type=TaskType.CODE, priority=TaskPriority.HIGH, status=TaskStatus.IN_PROGRESS,
            assigned_to="DEV-002", original_assignee="DEV-002", estimated_hours=6, progress=30,
            created_at=datetime.now(), tags=["frontend", "react"]
        ),
        # Charlie's tasks (He is present)
        Task(
            id="OPS-001", title="Configure CI/CD Pipeline", 
            description="Set up GitHub Actions for automated testing and deployment.",
            task_type=TaskType.CODE, priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED,
            assigned_to="DEV-003", original_assignee="DEV-003", estimated_hours=4, progress=0,
            created_at=datetime.now(), tags=["devops", "ci-cd"]
        )
    ]
    task_manager.load_tasks(tasks)
    
    return employees, tasks
