from datetime import datetime
from models.employee import Employee, SkillTag, WorkloadLevel
from models.task import Task, TaskPriority, TaskStatus, TaskType, SubTask
from tools import employee_db, task_manager, calendar_tool


def seed_employees():
    employees = [
        Employee(
            id="EMP-001",
            name="Riya Sharma",
            role="Backend Developer",
            department="Engineering",
            skills=[
                SkillTag(skill="Python", proficiency=0.95),
                SkillTag(skill="FastAPI", proficiency=0.90),
                SkillTag(skill="PostgreSQL", proficiency=0.85),
                SkillTag(skill="REST APIs", proficiency=0.90),
                SkillTag(skill="Docker", proficiency=0.70)
            ],
            workload=WorkloadLevel.HIGH,
            workload_score=75,
            is_available=True,
            is_absent=False,
            email="riya.sharma@company.com",
            avatar_color="#FF6B6B"
        ),
        Employee(
            id="EMP-002",
            name="Arjun Mehta",
            role="Senior Backend Developer",
            department="Engineering",
            skills=[
                SkillTag(skill="Python", proficiency=0.95),
                SkillTag(skill="Node.js", proficiency=0.80),
                SkillTag(skill="AWS", proficiency=0.85),
                SkillTag(skill="Docker", proficiency=0.90),
                SkillTag(skill="Kubernetes", proficiency=0.75)
            ],
            workload=WorkloadLevel.MEDIUM,
            workload_score=55,
            is_available=True,
            is_absent=False,
            email="arjun.mehta@company.com",
            avatar_color="#4ECDC4"
        ),
        Employee(
            id="EMP-003",
            name="Priya Nair",
            role="Frontend Developer",
            department="Engineering",
            skills=[
                SkillTag(skill="React", proficiency=0.95),
                SkillTag(skill="TypeScript", proficiency=0.90),
                SkillTag(skill="Tailwind", proficiency=0.85),
                SkillTag(skill="Figma", proficiency=0.80),
                SkillTag(skill="JavaScript", proficiency=0.95)
            ],
            workload=WorkloadLevel.LOW,
            workload_score=35,
            is_available=True,
            is_absent=False,
            email="priya.nair@company.com",
            avatar_color="#45B7D1"
        ),
        Employee(
            id="EMP-004",
            name="Karan Singh",
            role="Data Analyst",
            department="Analytics",
            skills=[
                SkillTag(skill="Python", proficiency=0.90),
                SkillTag(skill="SQL", proficiency=0.95),
                SkillTag(skill="Pandas", proficiency=0.90),
                SkillTag(skill="Tableau", proficiency=0.85),
                SkillTag(skill="Excel", proficiency=0.95)
            ],
            workload=WorkloadLevel.MEDIUM,
            workload_score=50,
            is_available=True,
            is_absent=False,
            email="karan.singh@company.com",
            avatar_color="#96CEB4"
        ),
        Employee(
            id="EMP-005",
            name="Meera Iyer",
            role="Product Manager",
            department="Product",
            skills=[
                SkillTag(skill="Roadmapping", proficiency=0.95),
                SkillTag(skill="Jira", proficiency=0.90),
                SkillTag(skill="Stakeholder Management", proficiency=0.95),
                SkillTag(skill="Product Strategy", proficiency=0.85),
                SkillTag(skill="Agile", proficiency=0.80)
            ],
            workload=WorkloadLevel.HIGH,
            workload_score=80,
            is_available=True,
            is_absent=False,
            email="meera.iyer@company.com",
            avatar_color="#DDA0DD"
        ),
        Employee(
            id="EMP-006",
            name="Rohan Das",
            role="DevOps Engineer",
            department="Engineering",
            skills=[
                SkillTag(skill="Docker", proficiency=0.95),
                SkillTag(skill="Kubernetes", proficiency=0.90),
                SkillTag(skill="CI/CD", proficiency=0.95),
                SkillTag(skill="AWS", proficiency=0.90),
                SkillTag(skill="Terraform", proficiency=0.80)
            ],
            workload=WorkloadLevel.MEDIUM,
            workload_score=45,
            is_available=True,
            is_absent=False,
            email="rohan.das@company.com",
            avatar_color="#F7DC6F"
        ),
        Employee(
            id="EMP-007",
            name="Anika Patel",
            role="UX Designer",
            department="Design",
            skills=[
                SkillTag(skill="Figma", proficiency=0.95),
                SkillTag(skill="User Research", proficiency=0.90),
                SkillTag(skill="Presentation Design", proficiency=0.85),
                SkillTag(skill="Prototyping", proficiency=0.90),
                SkillTag(skill="UI Design", proficiency=0.95)
            ],
            workload=WorkloadLevel.LOW,
            workload_score=30,
            is_available=True,
            is_absent=False,
            email="anika.patel@company.com",
            avatar_color="#BB8FCE"
        ),
        Employee(
            id="EMP-008",
            name="Vikram Rao",
            role="Engineering Manager",
            department="Engineering",
            skills=[
                SkillTag(skill="Python", proficiency=0.80),
                SkillTag(skill="Leadership", proficiency=0.95),
                SkillTag(skill="Code Review", proficiency=0.90),
                SkillTag(skill="Team Management", proficiency=0.95),
                SkillTag(skill="System Design", proficiency=0.85)
            ],
            workload=WorkloadLevel.MEDIUM,
            workload_score=60,
            is_available=True,
            is_absent=False,
            email="vikram.rao@company.com",
            avatar_color="#85C1E9"
        ),
        Employee(
            id="EMP-009",
            name="Sneha Kapoor",
            role="Marketing Analyst",
            department="Marketing",
            skills=[
                SkillTag(skill="Content Writing", proficiency=0.90),
                SkillTag(skill="Research", proficiency=0.85),
                SkillTag(skill="Excel", proficiency=0.90),
                SkillTag(skill="Data Analysis", proficiency=0.80),
                SkillTag(skill="Social Media", proficiency=0.75)
            ],
            workload=WorkloadLevel.MEDIUM,
            workload_score=55,
            is_available=True,
            is_absent=False,
            email="sneha.kapoor@company.com",
            avatar_color="#F8B195"
        ),
        Employee(
            id="EMP-010",
            name="Dev Sharma",
            role="Full Stack Developer",
            department="Engineering",
            skills=[
                SkillTag(skill="React", proficiency=0.90),
                SkillTag(skill="Python", proficiency=0.85),
                SkillTag(skill="MongoDB", proficiency=0.85),
                SkillTag(skill="Node.js", proficiency=0.90),
                SkillTag(skill="JavaScript", proficiency=0.95)
            ],
            workload=WorkloadLevel.HIGH,
            workload_score=70,
            is_available=True,
            is_absent=False,
            email="dev.sharma@company.com",
            avatar_color="#C9B1FF"
        )
    ]
    employee_db.load_employees(employees)
    return employees


def seed_tasks():
    tasks = [
        # Riya's tasks (EMP-001)
        Task(
            id="TASK-001",
            title="Implement JWT authentication middleware",
            description="Create a secure JWT authentication middleware for the FastAPI backend with token refresh functionality",
            task_type=TaskType.CODE,
            priority=TaskPriority.CRITICAL,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-001",
            original_assignee="EMP-001",
            estimated_hours=6,
            progress=60,
            created_at=datetime.now(),
            tags=["backend", "security", "fastapi"]
        ),
        Task(
            id="TASK-002",
            title="Fix payment gateway timeout bug",
            description="Investigate and fix the timeout issue in the payment gateway integration causing failed transactions",
            task_type=TaskType.CODE,
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-001",
            original_assignee="EMP-001",
            estimated_hours=4,
            progress=30,
            created_at=datetime.now(),
            tags=["backend", "bug", "payments"]
        ),
        Task(
            id="TASK-003",
            title="Write Q2 performance report",
            description="Compile and analyze team performance metrics for Q2 and prepare comprehensive report",
            task_type=TaskType.REPORT,
            priority=TaskPriority.HIGH,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-001",
            original_assignee="EMP-001",
            estimated_hours=3,
            progress=0,
            created_at=datetime.now(),
            tags=["documentation", "report"]
        ),
        Task(
            id="TASK-004",
            title="Prepare investor update presentation",
            description="Create a professional presentation for investors highlighting product progress and roadmap",
            task_type=TaskType.PRESENTATION,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-001",
            original_assignee="EMP-001",
            estimated_hours=8,
            progress=0,
            created_at=datetime.now(),
            tags=["presentation", "stakeholders"]
        ),
        Task(
            id="TASK-005",
            title="Database query optimization",
            description="Review and optimize slow-running database queries in the user service",
            task_type=TaskType.CODE,
            priority=TaskPriority.LOW,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-001",
            original_assignee="EMP-001",
            estimated_hours=5,
            progress=0,
            created_at=datetime.now(),
            tags=["database", "performance"]
        ),

        # Arjun's tasks (EMP-002)
        Task(
            id="TASK-006",
            title="Set up monitoring alerts for production",
            description="Configure CloudWatch alerts for all production services with appropriate thresholds",
            task_type=TaskType.CODE,
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-002",
            original_assignee="EMP-002",
            estimated_hours=4,
            progress=50,
            created_at=datetime.now(),
            tags=["devops", "monitoring", "aws"]
        ),
        Task(
            id="TASK-007",
            title="Refactor authentication service",
            description="Migrate the legacy authentication service to the new microservices architecture",
            task_type=TaskType.CODE,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-002",
            original_assignee="EMP-002",
            estimated_hours=8,
            progress=0,
            created_at=datetime.now(),
            tags=["backend", "refactor", "microservices"]
        ),
        Task(
            id="TASK-008",
            title="Create deployment pipeline documentation",
            description="Document the CI/CD pipeline setup and deployment procedures for new team members",
            task_type=TaskType.DOCUMENTATION,
            priority=TaskPriority.LOW,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-002",
            original_assignee="EMP-002",
            estimated_hours=2,
            progress=0,
            created_at=datetime.now(),
            tags=["documentation", "devops"]
        ),

        # Priya's tasks (EMP-003)
        Task(
            id="TASK-009",
            title="Implement dark mode toggle",
            description="Add dark mode feature to the web application with system preference detection",
            task_type=TaskType.CODE,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-003",
            original_assignee="EMP-003",
            estimated_hours=5,
            progress=70,
            created_at=datetime.now(),
            tags=["frontend", "react", "ui"]
        ),
        Task(
            id="TASK-010",
            title="Design system component library",
            description="Create reusable component library following the new design system guidelines",
            task_type=TaskType.CODE,
            priority=TaskPriority.HIGH,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-003",
            original_assignee="EMP-003",
            estimated_hours=10,
            progress=0,
            created_at=datetime.now(),
            tags=["frontend", "components", "design-system"]
        ),

        # Karan's tasks (EMP-004)
        Task(
            id="TASK-011",
            title="Build customer segmentation dashboard",
            description="Create Tableau dashboard for customer segmentation analysis",
            task_type=TaskType.CODE,
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-004",
            original_assignee="EMP-004",
            estimated_hours=6,
            progress=40,
            created_at=datetime.now(),
            tags=["analytics", "visualization", "tableau"]
        ),
        Task(
            id="TASK-012",
            title="Analyze user retention metrics",
            description="Run SQL queries to analyze user retention and churn rates for Q2",
            task_type=TaskType.RESEARCH,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-004",
            original_assignee="EMP-004",
            estimated_hours=4,
            progress=0,
            created_at=datetime.now(),
            tags=["analytics", "sql", "research"]
        ),
        Task(
            id="TASK-013",
            title="Automate weekly report generation",
            description="Create Python script to automate weekly analytics report generation",
            task_type=TaskType.CODE,
            priority=TaskPriority.LOW,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-004",
            original_assignee="EMP-004",
            estimated_hours=3,
            progress=0,
            created_at=datetime.now(),
            tags=["automation", "python", "analytics"]
        ),

        # Meera's tasks (EMP-005)
        Task(
            id="TASK-014",
            title="Q3 roadmap planning",
            description="Plan and document the product roadmap for Q3 including feature priorities",
            task_type=TaskType.DOCUMENTATION,
            priority=TaskPriority.CRITICAL,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-005",
            original_assignee="EMP-005",
            estimated_hours=5,
            progress=80,
            created_at=datetime.now(),
            tags=["product", "planning", "roadmap"]
        ),
        Task(
            id="TASK-015",
            title="Stakeholder interview preparation",
            description="Prepare materials and questions for upcoming stakeholder interviews",
            task_type=TaskType.RESEARCH,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-005",
            original_assignee="EMP-005",
            estimated_hours=2,
            progress=0,
            created_at=datetime.now(),
            tags=["product", "research", "stakeholders"]
        ),

        # Rohan's tasks (EMP-006)
        Task(
            id="TASK-016",
            title="Kubernetes cluster upgrade",
            description="Upgrade EKS cluster to latest version with zero downtime",
            task_type=TaskType.CODE,
            priority=TaskPriority.CRITICAL,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-006",
            original_assignee="EMP-006",
            estimated_hours=6,
            progress=0,
            created_at=datetime.now(),
            tags=["devops", "kubernetes", "aws"]
        ),
        Task(
            id="TASK-017",
            title="Implement disaster recovery plan",
            description="Create and document disaster recovery procedures for production systems",
            task_type=TaskType.DOCUMENTATION,
            priority=TaskPriority.HIGH,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-006",
            original_assignee="EMP-006",
            estimated_hours=4,
            progress=0,
            created_at=datetime.now(),
            tags=["devops", "documentation", "dr"]
        ),

        # Anika's tasks (EMP-007)
        Task(
            id="TASK-018",
            title="Redesign onboarding flow",
            description="Create new user onboarding experience based on recent UX research findings",
            task_type=TaskType.CODE,
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-007",
            original_assignee="EMP-007",
            estimated_hours=8,
            progress=25,
            created_at=datetime.now(),
            tags=["ux", "design", "figma"]
        ),
        Task(
            id="TASK-019",
            title="Conduct user testing sessions",
            description="Schedule and conduct user testing sessions for the new dashboard feature",
            task_type=TaskType.RESEARCH,
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.NOT_STARTED,
            assigned_to="EMP-007",
            original_assignee="EMP-007",
            estimated_hours=5,
            progress=0,
            created_at=datetime.now(),
            tags=["ux", "research", "testing"]
        ),

        # Vikram's tasks (EMP-008)
        Task(
            id="TASK-020",
            title="Code review for authentication module",
            description="Perform comprehensive code review of the new authentication module",
            task_type=TaskType.REVIEW,
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            assigned_to="EMP-008",
            original_assignee="EMP-008",
            estimated_hours=3,
            progress=60,
            created_at=datetime.now(),
            tags=["code-review", "backend", "security"]
        ),
    ]
    task_manager.load_tasks(tasks)
    return tasks


from .simulation_seeder import seed_ecommerce_project

def initialize_database():
    """Initialize the database with E-Commerce project data"""
    employees, tasks = seed_ecommerce_project()
    print(f"Project initialized: {len(employees)} employees, {len(tasks)} tasks.")
    return employees, tasks