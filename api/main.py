from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from routes.auth import auth_router
from db import connect_to_mongo, close_mongo_connection, get_database
from models import UserDataResponse
from jose import JWTError, jwt
from auth import get_password_hash, verify_password, create_refresh_token, create_access_token, get_current_user, credentials_exception
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes.projects import project_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.router.include_router(auth_router)
app.router.include_router(project_router)
@app.get("/users/me", response_model=UserDataResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserDataResponse(**current_user)
@app.get("/users/me/task-count")
async def get_task_state_distribution(state:str, current_user: dict = Depends(get_current_user)):
    
    """
    Show task state distribution for a project 
    """
    
    pipeline = [
        {
            "$match": {
                "assigned_to._id": current_user['_id'],
                "state": state
            }
        },
        {
            "$count": "nb_of_tasks"
        },
    ]
    return await get_database()["tasks"].aggregate(pipeline).to_list(length=None)

