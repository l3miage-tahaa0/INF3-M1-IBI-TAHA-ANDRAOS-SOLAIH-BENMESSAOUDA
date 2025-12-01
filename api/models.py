from pydantic import BaseModel, Field, EmailStr, GetCoreSchemaHandler
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        # Accept string → convert to ObjectId
        def validate(value):
            if isinstance(value, ObjectId):
                return value
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return ObjectId(value)

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema(
                    [
                        core_schema.str_schema(),
                        # VALIDATOR MUST BE IN PYTHON BRANCH ONLY
                        core_schema.general_plain_validator_function(validate),
                    ]
                ),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: str(v)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # JSON schema MUST NOT include validator functions
        return {"type": "string", "example": "60ad8f02c45e88b6f8e4b6e2"}


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
    first_name: str
    last_name: str
    class Config:
        schema_extra = {
            "example": {
                "email": "abdul@example.com",
                "first_name": "Abdul",
                "last_name": "Abdul"
            }
        }

class UserExtendedReference(BaseModel):
    id: PyObjectId = Field(alias="_id")
    first_name: str
    last_name: str
    email: EmailStr

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

#Task models
class ProjectExtendedReference(BaseModel):
    id: PyObjectId = Field(alias="_id")
    project_title: str

class Task(BaseModel):
    id: PyObjectId = Field(alias="_id")
    project: ProjectExtendedReference
    title: str
    description: str
    assigned_to: Optional[UserExtendedReference]
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
    """
    A model for all possible fields that can be updated on a task.
    All fields are optional, so clients only send what they want to change.
    """
    title: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = Field(None)
    priority: Optional[str] = Field(None) # Could be an Enum: "low", "medium", "high"
    state: Optional[str] = Field(None)
    assigned_to: Optional[UserExtendedReference] = Field(None)
    deadline: Optional[datetime] = Field(None)

    class Config:
        # Pydantic v2 feature to handle nested models properly
        json_schema_extra = {
            "example": {
                "priority": "high",
                "state": "in_progress"
            }
        }
# Project models
class Project(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    description: str
    managers: List[UserExtendedReference]
    members: List[UserExtendedReference]
    created_at: datetime

class CreateProjectRequest(BaseModel):
    title: str
    description: str

class CreateProjectResponse(BaseModel):
    id: str