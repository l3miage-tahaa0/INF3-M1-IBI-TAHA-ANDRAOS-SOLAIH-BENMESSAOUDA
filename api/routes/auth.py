from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from db import get_database
from models import CreateUserRequest, UserDataResponse, TokenSchema, LoginUserRequest
from jose import JWTError, jwt
from auth import get_password_hash, get_current_token, verify_password, create_refresh_token, create_access_token, get_current_user, credentials_exception
from config import settings
from pymongo.errors import DuplicateKeyError
auth_router = APIRouter(prefix="/auth")

@auth_router.post("/signup", response_model=UserDataResponse, status_code=status.HTTP_201_CREATED)
async def user_signup(user: CreateUserRequest):
    db = get_database()
    hashed_password = get_password_hash(user.password)
    user_in_db = user.model_dump()
    user_in_db["password"] = hashed_password
    try:
        await db["users"].insert_one(user_in_db)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    return user

@auth_router.post("/login", response_model=TokenSchema)
async def login(form_data: LoginUserRequest):
    db = get_database()
    user = await db["users"].find_one({"email": form_data.email})
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["email"]})

    # Hash the refresh token and store it in the database
    hashed_refresh_token = get_password_hash(refresh_token)
    await db["users"].update_one(
        {"_id": user["_id"]}, {"$set": {"hashed_refresh_token": hashed_refresh_token}}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@auth_router.get("/refresh", response_model=TokenSchema)
async def refresh_token(refresh_token: str = Depends(get_current_token)):
    db = get_database()
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = await db["users"].find_one({"email": email})

    if user is None or user.get("hashed_refresh_token") is None:
        raise credentials_exception

    # Verify the submitted refresh token against the hashed version in the DB
    if not verify_password(refresh_token, user["hashed_refresh_token"]):
        raise credentials_exception
    
    # Issue new tokens
    new_access_token = create_access_token(data={"sub": email})
    new_refresh_token = create_refresh_token(data={"sub": email})

    # Update the stored refresh token hash
    new_hashed_refresh_token = get_password_hash(new_refresh_token)
    await db["users"].update_one(
        {"_id": user["_id"]}, {"$set": {"hashed_refresh_token": new_hashed_refresh_token}}
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: dict = Depends(get_current_user)):
    db = get_database()
    # Remove the refresh token from the database to invalidate it
    await db["users"].update_one(
        {"_id": current_user["_id"]}, {"$set": {"hashed_refresh_token": None}}
    )
    return {"message": "Logout successful"}

