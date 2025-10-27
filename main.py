from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from db import connect_to_mongo, close_mongo_connection, get_database
from models import UserSchema, TokenSchema, UserInDB
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from config import settings
from pymongo.errors import DuplicateKeyError
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

@app.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def user_signup(user: UserSchema = Body(...)):
    db = get_database()
    hashed_password = get_password_hash(user.password)
    
    user_in_db = UserInDB(**user.model_dump(), hashed_password=hashed_password)
    
    try:
        await db["users"].insert_one(user_in_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    return user

@app.post("/login", response_model=TokenSchema)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_database()
    user = await db["users"].find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # The dependency already fetches and validates the user
    # We return a Pydantic model for response validation and to hide the hashed_password
    return UserSchema(**current_user)

