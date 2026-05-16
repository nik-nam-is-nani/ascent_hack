from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class WorkloadLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SkillTag(BaseModel):
    skill: str
    proficiency: float  # 0.0 to 1.0


class Employee(BaseModel):
    id: str
    name: str
    role: str
    department: str
    skills: List[SkillTag]
    workload: WorkloadLevel
    workload_score: int  # 0-100
    is_available: bool
    is_absent: bool
    email: str
    avatar_color: str
    current_tasks: List[str] = []
    created_at: datetime = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }