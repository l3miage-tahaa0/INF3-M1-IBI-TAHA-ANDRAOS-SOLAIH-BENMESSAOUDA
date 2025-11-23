from fastapi import APIRouter, Depends, HTTPException, status, Body

from datetime import datetime

from db import get_database
from models import Project, CreateProjectRequest, CreateTaskRequest, Task, CreateProjectResponse, CreateTaskResponse, TaskUpdate
from auth import get_current_user
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from bson import ObjectId
from pydantic import BaseModel

project_router = APIRouter(prefix="/projects")

@project_router.get("/", response_model=list[Project])
async def get_projects(current_user: dict = Depends(get_current_user)):
    return await get_database()["projects"].find({
        "$or": [
            { "members._id": current_user["_id"] },
            { "managers._id": current_user["_id"] }
        ]
    }).to_list()
@project_router.get("/{id}", response_model=Project)
async def get_project(id: str, current_user: dict = Depends(get_current_user)):
    project = await get_database()["projects"].find_one({
        "_id": ObjectId(id),
        "$or": [
            { "members._id": current_user["_id"] },
            { "managers._id": current_user["_id"] }
        ]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@project_router.post("/", response_model=CreateProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: CreateProjectRequest, current_user: dict = Depends(get_current_user)):
    project_doc = {
        "title": project.title,
        "description": project.description,
        "managers": [{
            "_id": current_user["_id"],
            "first_name": current_user["first_name"],
            "last_name": current_user["last_name"],
            "email": current_user["email"]
        }],
        "members": [],
        "created_at": datetime.now()
    }
    result = await get_database()["projects"].insert_one(project_doc)
    print(f"Created project '{project.title}'")
    return CreateProjectResponse(id=str(result.inserted_id))

async def is_project_manager(project_id: str, user_id: str):
    project = await get_database()["projects"].find_one({
        "_id": project_id,
        "managers._id": user_id
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@project_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: str, current_user: dict = Depends(get_current_user)):
    # Check if user is project manager
    project = await is_project_manager(ObjectId(id), current_user["_id"])
    await get_database()["projects"].delete_one({"_id": project["_id"]})
    print(f"Deleted project '{project['title']}'")
    return

@project_router.post("/{id}/members/{user_email}", response_model=Project)
async def add_project_member(id: str, user_email: str, current_user: dict = Depends(get_current_user)):
    # Check if user is project manager
    project = await is_project_manager(ObjectId(id), ObjectId(current_user["_id"]))
    # Check if user isn't already a member or manager
    user = await get_database()["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if any(member["_id"] == user["_id"] for member in project["members"]) or any(manager["_id"] == user["_id"] for manager in project["managers"]):
        raise HTTPException(status_code=400, detail="User is already a member or manager of the project")
    await get_database()["projects"].update_one(
        {"_id": project["_id"]},
        {"$addToSet": {"members": {
            "_id": user["_id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"]
        }}}
    )
    print(f"Added user '{user['first_name']} {user['last_name']}' to project '{project['title']}'")
    return project

@project_router.delete("/{id}/members/{user_email}", response_model=Project)
async def remove_project_member(id: str, user_email: str, current_user: dict = Depends(get_current_user)):

    # Check if user is project manager
    project = await is_project_manager(ObjectId(id), ObjectId(current_user["_id"]))
    #Check if user is a member
    if not any(member["email"] == user_email for member in project["members"]):
        raise HTTPException(status_code=400, detail="User is not a member of the project")
    await get_database()["projects"].update_one(
        {"_id": project["_id"]},
        {"$pull": {"members": {"email": user_email}}}
    )
    print(f"Removed user '{user_email}' from project '{project['title']}'")
    return project

@project_router.delete("/{id}/managers/{user_email}", response_model=Project)
async def remove_project_manager(id: str, user_email: str, current_user: dict = Depends(get_current_user)):

    # Check if user is project manager
    project = await is_project_manager(ObjectId(id), ObjectId(current_user["_id"]))
    #Check if user is a member
    user = await get_database()["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(manager["_id"] == ObjectId(user["_id"]) for manager in project["managers"]):
        raise HTTPException(status_code=400, detail="User is not a manager of the project")
    await get_database()["projects"].update_one(
        {"_id": project["_id"]},
        {"$addToSet": {"members": {
            "_id": user["_id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"]
        }},
        "$pull": {"managers": {"email":user_email}}}
    )
    print(f"Removed user '{user_email}' from project '{project['title']}'")
    return project

@project_router.post("/{id}/managers/{user_email}", response_model=Project)
async def add_project_manager(id: str, user_email: str, current_user: dict = Depends(get_current_user)):
    # Check if user is project manager
    project = await is_project_manager(ObjectId(id), ObjectId(current_user["_id"]))
    # Check if user exists
    user = await get_database()["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Check if user isn't a manager already
    if any(manager["_id"] == user["_id"] for manager in project["managers"]):
        raise HTTPException(status_code=400, detail="User is already a manager of the project")
    # Check if user isn't a member already
    if not any(member["_id"] == user["_id"] for member in project["members"]):
        raise HTTPException(status_code=400, detail="User isn't already a member of the project")
    #add to managers and remove from members
    await get_database()["projects"].update_one(
        {"_id": project["_id"]},
        {
            "$addToSet": {"managers": {
                "_id": user["_id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"]
            }},
            "$pull": {"members": {"_id": user["_id"]}}
        }
    )
    print(f"Added user '{user['first_name']} {user['last_name']}' to project '{project['title']}'")
    return project

#TASKS
@project_router.post("/{id}/tasks/", response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(id: str, task: CreateTaskRequest, current_user: dict = Depends(get_current_user)):
    # Check if user is project manager
    project = await is_project_manager(ObjectId(id), current_user["_id"])

    task_doc = {
        "title": task.title,
        "description": task.description,
        "project": {
            "_id": project["_id"],
            "project_title": project["title"]
        },
        "assigned_to": None,
        "state": "Not Started",
        "priority": task.priority,
        "deadline": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    result = await get_database()["tasks"].insert_one(task_doc)
    print(f"Created task '{task.title}'")
    return CreateTaskResponse(id=str(result.inserted_id))

# @project_router.put("/{id}/tasks/{task_id}/state", response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED)
# async def update_task_state(id: str, task_id: str, current_user: dict = Depends(get_current_user)):
#     # Check if user is project manager
#     project = await is_project_manager(ObjectId(id), current_user["_id"])
#     task = await get_database()["tasks"].find_one({
#         "_id": ObjectId(task_id),
#         "project._id": project["_id"]
#     })
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
@project_router.patch("/{project_id}/tasks/{task_id}", response_model=Task)
async def update_task(
    project_id: str,
    task_id: str,
    update_data: TaskUpdate,
    current_user = Depends(get_current_user)
):
    """
    Modularly update a task.
    - Managers can update any field.
    - Assigned users can only update the 'state' field (with restrictions).
    """
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID format.")

    #Fetch original task and its project to check permissions
    task = await db["tasks"].find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    
    if task["project"]["_id"] != ObjectId(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task does not belong to the specified project.")
    
    project = await db["projects"].find_one({"_id": task["project"]["_id"]})
    
    if not project:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Associated project not found.")

    #Determine user's role for this task
    is_manager = any(m["_id"] == current_user["_id"] for m in project.get("managers", []))
    # Safely determine if current_user is the assigned user. Accept both '_id' and 'id' shapes.
    assigned_to = task.get("assigned_to")
    assigned_id = None
    if isinstance(assigned_to, dict):
        if "_id" in assigned_to:
            assigned_id = assigned_to["_id"]
        elif "id" in assigned_to:
            try:
                assigned_id = ObjectId(assigned_to["id"]) if ObjectId.is_valid(assigned_to["id"]) else assigned_to["id"]
            except Exception:
                assigned_id = assigned_to["id"]
    is_assigned_user = assigned_id is not None and assigned_id == current_user["_id"]

    # Build the MongoDB update document based on permissions
    update_fields = update_data.model_dump(exclude_unset=True)

    # Normalize assigned_to payload: client may send { id: '...' } (frontend uses 'id'),
    # but our Pydantic model expects alias '_id'. If present, rename 'id' -> '_id'.
    if 'assigned_to' in update_fields and update_fields['assigned_to'] is not None:
        at = update_fields['assigned_to']
        # if it's a mapping and contains 'id' but not '_id', rename it
        if isinstance(at, dict) and 'id' in at and '_id' not in at:
            at['_id'] = ObjectId(at['id']) if ObjectId.is_valid(at['id']) else at['id']
            del at['id']
        update_fields['assigned_to'] = at
    
    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body cannot be empty.")

    update_doc = {}

    for field, value in update_fields.items():
        # A. Check permissions for changing the 'state'
        if field == "state":
            if is_manager:
                update_doc["state"] = value
            elif is_assigned_user:
                if value == "COMPLETED":
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only a project manager can complete a task.")
                update_doc["state"] = value
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to change this task's state.")
        
        # B. Check permissions for all other manager-only fields
        elif field in ["title", "description", "priority", "assigned_to"]:
            if not is_manager:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Only a project manager can update the task's {field}.")
            # Convert Pydantic model to dict for MongoDB
            update_doc[field] = value if not isinstance(value, BaseModel) else value.model_dump()
        
        else:
            # If a field is not recognized, ignore or raise an error
            pass 


    # 4. Perform the atomic database update if there are changes
    if not update_doc:
        # This can happen if a non-manager/non-assigned user tries to update state
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to modify any of the requested fields.")
    update_doc["updated_at"] = datetime.now()
    updated_task = await db["tasks"].find_one_and_update(
        {"_id": ObjectId(task_id)},
        {"$set": update_doc},
        return_document=ReturnDocument.AFTER
    )
    return updated_task

@project_router.get("/{id}/tasks/", response_model=list[Task])
async def get_project_tasks(id: str, current_user: dict = Depends(get_current_user)):
    # Check if user is project member or manager
    project = await get_database()["projects"].find_one({
        "_id": ObjectId(id),
        "$or": [
            { "members._id": current_user["_id"] },
            { "managers._id": current_user["_id"] }
        ]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = await get_database()["tasks"].find({
        "project._id": project["_id"]
    }).to_list()
    return tasks

@project_router.get("/{project_id}/tasks/{task_id}", response_model=Task)
async def get_task(project_id: str, task_id: str, current_user: dict = Depends(get_current_user)):
    # Check if user is project member or manager
    project = await get_database()["projects"].find_one({
        "_id": ObjectId(project_id),
        "$or": [
            { "members._id": current_user["_id"] },
            { "managers._id": current_user["_id"] }
        ]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    task = await get_database()["tasks"].find_one({
        "_id": ObjectId(task_id),
        "project._id": project["_id"]
    })
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@project_router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(project_id: str, task_id: str, current_user: dict = Depends(get_current_user)):
    # Check if user is project manager
    project = await is_project_manager(ObjectId(project_id), ObjectId(current_user["_id"]))
    task = await get_database()["tasks"].find_one({
        "_id": ObjectId(task_id),
        "project._id": project["_id"]
    })
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await get_database()["tasks"].delete_one({"_id": task["_id"]})
    print(f"Deleted task '{task['title']}' from project '{project['title']}'")
    return