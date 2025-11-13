from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

# User/AUTH models
class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    class Config:
        schema_extra = {
            "example": {
                "email": "abdul@example.com",
                "password": "password",
                "first_name": "Abdul",
                "last_name": "Abdul"
            }
        }

class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str
    class Config:
        schema_extra = {
            "example": {
                "email": "abdul@example.com",
                "password": "password"
            }
        }

class UserDataResponse(BaseModel):
    email: EmailStr
    class Config:
        schema_extra = {
            "example": {
                "email": "abdul@example.com"
            }
        }

class UserExtendedReference(BaseModel):
    _id: ObjectId
    first_name: ObjectId
    last_name: ObjectId

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

#Task models
class ProjectExtendedReference(BaseModel):
    projectId: ObjectId
    projectName: str

class Task:
    _id: ObjectId
    project: ProjectExtendedReference
    title: str
    description: str
    assignedTo: Optional[UserExtendedReference]
    state: str
    priority: str
    deadline: datetime
    created_at: datetime
    updated_at: datetime

# Project models
class Project(BaseModel):
    _id: ObjectId
    title: str
    description: str
    managers: List[UserExtendedReference]
    members: List[UserExtendedReference]
    created_at: datetime

class CreateProjectRequest(BaseModel):
    title: str
    description: str