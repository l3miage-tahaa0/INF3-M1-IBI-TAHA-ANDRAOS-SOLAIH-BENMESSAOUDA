from pydantic import BaseModel, Field, EmailStr
from typing import Optional

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