from datetime import datetime
from models.employee import Employee, SkillTag, WorkloadLevel
from models.task import Task, TaskPriority, TaskStatus, TaskType
from tools import employee_db, task_manager, calendar_tool
from tools.workspace_tool import write_to_workspace

def seed_ecommerce_project():
    """Seed the 10-person Mini E-Commerce Project simulation"""

    # Check if database already has data - only seed if empty
    from tools.employee_db import is_database_empty

    if not is_database_empty():
        # Database already has data, return existing employees and tasks
        employees = employee_db.get_all_employees()
        tasks = task_manager.get_all_tasks()
        return employees, tasks
    
    # 2. Add 10 specialized employees
    employees = [
        Employee(id="P1", name="Riya Sharma", role="UI Developer", department="Frontend",
                 skills=[SkillTag(skill="React", proficiency=0.9), SkillTag(skill="CSS", proficiency=0.85)],
                 workload=WorkloadLevel.MEDIUM, workload_score=50, is_available=True, is_absent=False,
                 email="riya@ecommerce.ai", avatar_color="#6366f1"),
        Employee(id="P2", name="Arjun Mehta", role="Frontend Lead", department="Frontend",
                 skills=[SkillTag(skill="React", proficiency=0.95), SkillTag(skill="Layouts", proficiency=0.9)],
                 workload=WorkloadLevel.HIGH, workload_score=80, is_available=True, is_absent=False,
                 email="arjun@ecommerce.ai", avatar_color="#10b981"),
        Employee(id="P3", name="Priya Nair", role="Frontend Dev", department="Frontend",
                 skills=[SkillTag(skill="JavaScript", proficiency=0.9), SkillTag(skill="APIs", proficiency=0.8)],
                 workload=WorkloadLevel.MEDIUM, workload_score=40, is_available=True, is_absent=False,
                 email="priya@ecommerce.ai", avatar_color="#f59e0b"),
        Employee(id="P4", name="Karan Singh", role="Frontend Dev", department="Frontend",
                 skills=[SkillTag(skill="React", proficiency=0.85), SkillTag(skill="State Mgmt", proficiency=0.9)],
                 workload=WorkloadLevel.LOW, workload_score=20, is_available=True, is_absent=False,
                 email="karan@ecommerce.ai", avatar_color="#ec4899"),
        Employee(id="P5", name="Meera Iyer", role="Frontend Dev", department="Frontend",
                 skills=[SkillTag(skill="React", proficiency=0.8), SkillTag(skill="UI Components", proficiency=0.9)],
                 workload=WorkloadLevel.MEDIUM, workload_score=45, is_available=True, is_absent=False,
                 email="meera@ecommerce.ai", avatar_color="#8b5cf6"),
        Employee(id="P6", name="Rohan Das", role="UI/UX Dev", department="Frontend",
                 skills=[SkillTag(skill="Tailwind", proficiency=0.9), SkillTag(skill="Forms", proficiency=0.85)],
                 workload=WorkloadLevel.HIGH, workload_score=75, is_available=True, is_absent=False,
                 email="rohan@ecommerce.ai", avatar_color="#06b6d4"),
        Employee(id="P7", name="Anika Patel", role="Frontend Dev", department="Frontend",
                 skills=[SkillTag(skill="React", proficiency=0.9), SkillTag(skill="Auth", proficiency=0.8)],
                 workload=WorkloadLevel.LOW, workload_score=30, is_available=True, is_absent=False,
                 email="anika@ecommerce.ai", avatar_color="#f97316"),
        Employee(id="P8", name="Vikram Rao", role="Full Stack", department="Core",
                 skills=[SkillTag(skill="Node.js", proficiency=0.9), SkillTag(skill="Express", proficiency=0.85)],
                 workload=WorkloadLevel.MEDIUM, workload_score=60, is_available=True, is_absent=False,
                 email="vikram@ecommerce.ai", avatar_color="#ef4444"),
        Employee(id="P9", name="Sneha Kapoor", role="Backend Dev", department="Backend",
                 skills=[SkillTag(skill="Auth", proficiency=0.95), SkillTag(skill="JWT", proficiency=0.9)],
                 workload=WorkloadLevel.HIGH, workload_score=85, is_available=True, is_absent=False,
                 email="sneha@ecommerce.ai", avatar_color="#22c55e"),
        Employee(id="P10", name="Dev Sharma", role="Backend Lead", department="Backend",
                 skills=[SkillTag(skill="Database", proficiency=0.9), SkillTag(skill="Server Integration", proficiency=0.95)],
                 workload=WorkloadLevel.MEDIUM, workload_score=55, is_available=True, is_absent=False,
                 email="dev@ecommerce.ai", avatar_color="#64748b"),
    ]
    employee_db.load_employees(employees)
    
    # 3. Add 10 specialized tasks
    tasks = [
        Task(id="TASK-P1", title="Homepage Design", 
             description="Create landing page UI including Navbar, Banner, and Category cards.",
             task_type=TaskType.CODE, priority=TaskPriority.HIGH, status=TaskStatus.NOT_STARTED,
             assigned_to="P1", original_assignee="P1", estimated_hours=6, progress=0,
             created_at=datetime.now(), tags=["frontend", "homepage"]),
        Task(id="TASK-P2", title="Product Listing Grid", 
             description="Display products in a grid layout with images, prices, and cart buttons.",
             task_type=TaskType.CODE, priority=TaskPriority.HIGH, status=TaskStatus.NOT_STARTED,
             assigned_to="P2", original_assignee="P2", estimated_hours=5, progress=0,
             created_at=datetime.now(), tags=["frontend", "products"]),
        Task(id="TASK-P3", title="Search Feature", 
             description="Implement live search filtering by name and category.",
             task_type=TaskType.CODE, priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED,
             assigned_to="P3", original_assignee="P3", estimated_hours=4, progress=0,
             created_at=datetime.now(), tags=["frontend", "search"]),
        Task(id="TASK-P4", title="Cart System", 
             description="Implement add/remove items, quantity updates, and total calculation.",
             task_type=TaskType.CODE, priority=TaskPriority.CRITICAL, status=TaskStatus.NOT_STARTED,
             assigned_to="P4", original_assignee="P4", estimated_hours=6, progress=0,
             created_at=datetime.now(), tags=["frontend", "cart"]),
        Task(id="TASK-P5", title="Wishlist System", 
             description="Allow users to save items to wishlist and move them to cart.",
             task_type=TaskType.CODE, priority=TaskPriority.LOW, status=TaskStatus.NOT_STARTED,
             assigned_to="P5", original_assignee="P5", estimated_hours=4, progress=0,
             created_at=datetime.now(), tags=["frontend", "wishlist"]),
        Task(id="TASK-P6", title="Payment & Checkout UI", 
             description="Create payment form, address form, and order summary.",
             task_type=TaskType.CODE, priority=TaskPriority.HIGH, status=TaskStatus.NOT_STARTED,
             assigned_to="P6", original_assignee="P6", estimated_hours=5, progress=0,
             created_at=datetime.now(), tags=["frontend", "payment"]),
        Task(id="TASK-P7", title="User Profile Dashboard", 
             description="Implement user details, order history, and edit profile features.",
             task_type=TaskType.CODE, priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED,
             assigned_to="P7", original_assignee="P7", estimated_hours=4, progress=0,
             created_at=datetime.now(), tags=["frontend", "profile"]),
        Task(id="TASK-P8", title="Admin Product Management", 
             description="Build dashboard to upload, edit, and delete products.",
             task_type=TaskType.CODE, priority=TaskPriority.HIGH, status=TaskStatus.NOT_STARTED,
             assigned_to="P8", original_assignee="P8", estimated_hours=6, progress=0,
             created_at=datetime.now(), tags=["admin", "backend"]),
        Task(id="TASK-P9", title="JWT Authentication", 
             description="Implement Login, Register, and JWT session handling.",
             task_type=TaskType.CODE, priority=TaskPriority.CRITICAL, status=TaskStatus.NOT_STARTED,
             assigned_to="P9", original_assignee="P9", estimated_hours=5, progress=0,
             created_at=datetime.now(), tags=["backend", "auth"]),
        Task(id="TASK-P10", title="Backend Integration", 
             description="Connect frontend/backend, setup database connection and API handling.",
             task_type=TaskType.CODE, priority=TaskPriority.HIGH, status=TaskStatus.NOT_STARTED,
             assigned_to="P10", original_assignee="P10", estimated_hours=6, progress=0,
             created_at=datetime.now(), tags=["backend", "integration"]),
    ]
    task_manager.load_tasks(tasks)
    
    return employees, tasks
