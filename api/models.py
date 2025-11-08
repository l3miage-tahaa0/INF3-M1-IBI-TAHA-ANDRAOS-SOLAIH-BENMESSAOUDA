from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List

#ProjectUser models
class ProjectUser(BaseModel):
    id: str
    project_id: str
    title: str
    access_role: str
    added_at: Optional[datetime]
class UserSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "abdul@example.com",
                "password": "password"
            }
        }
class UserDataResponse(BaseModel):
    email: EmailStr = Field(...)
    projects: List[ProjectUser]
    class Config:
        schema_extra = {
            "example": {
                "email": "abdul@example.com"
            }
        }

class UserInDB(UserSchema):
    hashed_password: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Project models
class Project(BaseModel):
    id: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime

class CreateProjectRequest(BaseModel):
    title: str
    description: str

