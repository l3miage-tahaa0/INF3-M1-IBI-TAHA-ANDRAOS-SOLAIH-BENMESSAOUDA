from fastapi import APIRouter, Depends, HTTPException, status, Body

from datetime import timedelta

from db import get_database
from models import UserInDB, Project
from config import settings
from auth import get_current_user
from pymongo.errors import DuplicateKeyError
project_router = APIRouter(prefix="/projects")

@project_router.get("/")
async def get_projects(current_user: dict = Depends(get_current_user)):
    return current_user['projects']