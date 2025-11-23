from pydantic import BaseModel, Field, EmailStr, GetCoreSchemaHandler
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic_core import CoreSchema, core_schema

# This is the custom Pydantic type for MongoDB's ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        This method defines how Pydantic should handle this custom type.
        It allows validation from a string and serialization to a string.
        """
        # Validator: Allows Pydantic to accept a string and convert it to an ObjectId
        def validate_from_str(value: str) -> ObjectId:
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return ObjectId(value)

        # Schema for validation from a Python ObjectId instance
        from_python_schema = core_schema.is_instance_schema(ObjectId)

        # Schema for validation from a string
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        # The final schema allows validation from either a string or an ObjectId instance
        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema([from_python_schema, from_str_schema]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

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