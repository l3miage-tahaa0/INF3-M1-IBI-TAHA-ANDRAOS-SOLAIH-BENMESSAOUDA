from pydantic import BaseModel, Field, EmailStr, GetCoreSchemaHandler
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pydantic_core import core_schema
from enum import Enum

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

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
