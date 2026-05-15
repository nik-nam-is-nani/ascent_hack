from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REASSIGNED = "reassigned"
    AUTO_COMPLETED = "auto_completed"
    BLOCKED = "blocked"


class TaskType(str, Enum):
    CODE = "code"
    PRESENTATION = "presentation"
    RESEARCH = "research"
    REPORT = "report"
    DOCUMENTATION = "documentation"
    MEETING = "meeting"
    REVIEW = "review"


class SubTask(BaseModel):
    id: str
    title: str
    description: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.NOT_STARTED


class Task(BaseModel):
    id: str
    title: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    assigned_to: str
    original_assignee: str  # who it was originally assigned to
    estimated_hours: float
    progress: int  # 0-100
    created_at: datetime = None
    due_date: Optional[str] = None
    tags: List[str] = []
    subtasks: List[SubTask] = []
    artifacts: List[str] = []  # URLs or references to created artifacts
    decision_reason: Optional[str] = None
    confidence_score: Optional[float] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Decision(BaseModel):
    task_id: str
    decision_type: str  # "reassign", "auto_complete", "split_and_reassign"
    assigned_to: Optional[str] = None
    confidence: float
    reasoning: str
    alternative_options: List[str] = []
    timestamp: datetime = None


class TaskManifest(BaseModel):
    tasks: List[Task]
    decisions: List[Decision]
    generated_at: datetime = None
    absent_employee_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }