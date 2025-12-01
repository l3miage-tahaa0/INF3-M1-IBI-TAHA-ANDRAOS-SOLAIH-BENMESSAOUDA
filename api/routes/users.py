from fastapi import APIRouter, Depends

from db import get_database
from models import UserDataResponse
from auth import get_current_user

user_router = APIRouter(prefix="/users")

@user_router.get("/me", response_model=UserDataResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserDataResponse(**current_user)

@user_router.get("/me/task-count")
async def get_task_state_distribution(state:str, current_user: dict = Depends(get_current_user)):
    
    """
    Show task state distribution for a user 
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