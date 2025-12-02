from pydantic import BaseModel, Field, EmailStr, GetCoreSchemaHandler
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic_core import core_schema
from enum import Enum
from models.utils import PyObjectId

class ProjectUserRole(str,Enum):
    MEMBER = "member"
    MANAGER = "manager"

class ProjectUserExtendedReference(BaseModel):
    id: PyObjectId = Field(alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    role: ProjectUserRole

class ProjectExtendedReference(BaseModel):
    id: PyObjectId = Field(alias="_id")
    project_title: str

class Project(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    description: str
    members: List[ProjectUserExtendedReference]
    created_at: datetime

class CreateProjectRequest(BaseModel):
    title: str
    description: str

class CreateProjectResponse(BaseModel):
    id: str