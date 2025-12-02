from models.utils import PyObjectId
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from models.project import ProjectExtendedReference

class TaskUserExtendedReference(BaseModel):
    id: PyObjectId = Field(alias="_id")
    first_name: str
    last_name: str
    email: EmailStr

class TaskState(str,Enum):
    NOT_STARTED = "NOT STARTED"
    IN_PROGRESS = "IN PROGRESS"
    SUBMITTED_FOR_VALIDATION = "SUBMITTED FOR VALIDATION"
    COMPLETED = "COMPLETED"

class TaskPriority(str,Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Task(BaseModel):
    id: PyObjectId = Field(alias="_id")
    project: ProjectExtendedReference
    title: str
    description: str
    assigned_to: Optional[TaskUserExtendedReference]
    state: str
    priority: str
    deadline: datetime
    created_at: datetime
    updated_at: datetime
class CreateTaskRequest(BaseModel):
    title: str
    description: str
    priority: str
    deadline: Optional[datetime]

class CreateTaskResponse(BaseModel):
    id: str

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = Field(None)
    priority: Optional[TaskPriority] = Field(None) 
    state: Optional[TaskState] = Field(None)
    assigned_to: Optional[TaskUserExtendedReference] = Field(None)
    deadline: Optional[datetime] = Field(None)

    class Config:
        json_schema_extra = {
            "example": {
                "priority": "high",
                "state": "in_progress"
            }
        }