from fastapi import APIRouter, Depends, HTTPException, status, Body
import logging

from datetime import datetime
from db import get_database
from services.auth import get_current_user
from pymongo import ReturnDocument
from bson import ObjectId
from models.project import Project, CreateProjectRequest, CreateProjectResponse
from models.task import Task, CreateTaskRequest, CreateTaskResponse, TaskUpdate

logger = logging.getLogger("inf3-projet-api")

from pydantic import BaseModel

project_router = APIRouter(prefix="/projects")


async def _fetch_project_for_user(project_id: str, current_user: dict):
    """
    Internal helper: return the project document if the current user is
    either a member or a manager. Raises HTTPException(404) if not found
    or not accessible.
    """
    try:
        pid = ObjectId(project_id) if not isinstance(project_id, ObjectId) else project_id
    except Exception:
        pid = project_id
    project = await get_database()["projects"].find_one({
        "_id": pid,
        "members._id": current_user["_id"]
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@project_router.get("/", response_model=list[Project])
async def get_projects(current_user: dict = Depends(get_current_user)):
    """
    Retrieve all projects for the current user.

    Returns a list of projects where the current user is either a member
    or a manager.
    """
    return await get_database()["projects"].find({
        "members._id": current_user["_id"]
    }).to_list()

@project_router.get("/{id}", response_model=Project)
async def get_project(id: str, current_user: dict = Depends(get_current_user)):
    """
    Retrieve a single project by ID for the current user.

    Returns the project if the current user is a member or manager.
    Raises 404 if not found or not accessible.
    """
    return await _fetch_project_for_user(id, current_user)

@project_router.get("/{id}/total-tasks")
async def get_total_tasks_per_project(id:str, current_user: dict = Depends(get_current_user)):
    """
    Return the total number of tasks for the specified project.

    Verifies the current user has access to the project and then
    runs an aggregation on the `tasks` collection to count tasks
    that reference the given project ID.
    """
    await _fetch_project_for_user(id, current_user)
    
    pipeline = [
        {"$match": {"project._id": ObjectId(id)}},
        {"$count": "total_tasks"}
    ]
    return await get_database()["tasks"].aggregate(pipeline).to_list(None)

@project_router.get("/{id}/tasks-state-priority-breakdown")
async def get_tasks_by_state_priority(id:str, current_user: dict = Depends(get_current_user)):
    """
    Provide a breakdown of tasks grouped by state and priority.

    Ensures the user can access the project, then groups tasks
    by their `state` and `priority` and returns counts.
    """
    await _fetch_project_for_user(id, current_user)
    
    pipeline = [
        {"$match": {"project._id": ObjectId(id)}},
        {   
            "$group": {
                "_id": {
                    "state": "$state",
                    "priority": "$priority"
                },
                "number_task": {"$sum": 1}
            }
        }
    ]
    return await get_database()["tasks"].aggregate(pipeline).to_list(length=None)


@project_router.get("/{id}/tasks-productivity")
async def get_top_productive_users(id:str,limit:int = 5,  current_user: dict = Depends(get_current_user)):
    """
    Return the top N users by number of completed tasks in the project.

    Validates access, filters tasks in state "COMPLETED", groups by
    the assignee and returns the top `limit` results sorted by count.
    """
    await _fetch_project_for_user(id, current_user)
    pipeline = [
        {
            "$match": {
                "project._id": ObjectId(id),
                "state": "COMPLETED",
                "assigned_to._id": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": {
                    "user_id": {"$toString": "$assigned_to._id"},
                    "first_name": "$assigned_to.first_name"
                },
                "tasks_completed": {"$sum": 1}
            }
        },
        {
            "$project":{
                "_id":0,
                "first_name":"$_id.first_name",
                "tasks_completed": 1
            }
        },
        {"$sort": {"tasks_completed": -1}},
        {"$limit": limit}
    ]
    return await get_database()["tasks"].aggregate(pipeline).to_list(length=None)

@project_router.get("/{id}/tasks-state-distribution")
async def get_task_state_distribution(id:str,  current_user: dict = Depends(get_current_user)):
    """
    Compute the distribution of task states for the project.

    After access validation, aggregates counts per task state and computes
    the percentage share of each state relative to the project's total tasks.
    """
    await _fetch_project_for_user(id, current_user)
    
    pipeline = [
        {"$match": {"project._id": ObjectId(id)}},

        {
            "$group": {
                "_id": "$state",
                "nb_of_tasks": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_task_count": {"$sum": "$nb_of_tasks"},
                "states": {
                    "$push": {
                        "state": "$_id",
                        "nb_of_tasks": "$nb_of_tasks"
                    }
                }
            }
        },
        {"$unwind": "$states"},
        {
            "$project": {
                "_id": 0,
                "state": "$states.state",
                "nb_of_tasks": "$states.nb_of_tasks",
                "percentage": {
                    "$multiply": [
                        { "$divide": ["$states.nb_of_tasks", "$total_task_count"] },
                        100
                    ]
                }
            }
        }
    ]
    return await get_database()["tasks"].aggregate(pipeline).to_list(length=None)

@project_router.get("/{id}/near-deadline")
async def get_tasks_near_deadline(id: str, inXDays:int = 3, current_user: dict = Depends(get_current_user)):
    """
    Get tasks whose deadline is within the next 3 days and not completed
    """
    await _fetch_project_for_user(id, current_user)

    from datetime import datetime, timedelta
    now = datetime.now()
    in_X_days = now + timedelta(days=inXDays)

    pipeline = [
        {
            "$match": {
                "project._id": ObjectId(id),
                "state": { "$ne": "COMPLETED" },
                "deadline": { "$gte": now, "$lte": in_X_days }
            }
        },
        {
            "$sort": { "deadline": 1 }
        }
    ]

    return await get_database()["tasks"].aggregate(pipeline).to_list(length=None)

@project_router.post("/", response_model=CreateProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: CreateProjectRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new project with the current user as its initial manager.

    Inserts a project document and returns the newly created project's ID.
    """
    project_doc = {
        "title": project.title,
        "description": project.description,
        "members": [{
            "_id": current_user["_id"],
            "first_name": current_user["first_name"],
            "last_name": current_user["last_name"],
            "email": current_user["email"],
            "role": "manager"
        }],
        "created_at": datetime.now()
    }
    result = await get_database()["projects"].insert_one(project_doc)
    logger.info(f"Created project '{project.title}'")
    return CreateProjectResponse(id=str(result.inserted_id))

async def is_project_manager(project_id: str, user_id: str):
    """
    Helper to verify whether a user is a manager for a given project.

    Expects `project_id` and `user_id` to be ObjectId-compatible. Raises
    404 if the project isn't found or the user isn't a manager. Returns
    the project document on success.
    """
    try:
        pid = ObjectId(project_id) if not isinstance(project_id, ObjectId) else project_id
    except Exception:
        pid = project_id
    try:
        uid = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
    except Exception:
        uid = user_id
    project = await get_database()["projects"].find_one({
        "_id": pid,
        "members": {"$elemMatch": {"_id": uid, "role": "manager"}}
    })
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@project_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a project (manager-only action).

    Confirms the current user is a project manager and deletes the
    project document. Returns no content on success.
    """

    project = await is_project_manager(ObjectId(id), current_user["_id"])
    deleted_tasks_result = await get_database()["tasks"].delete_many({"project._id": project["_id"]})
    await get_database()["projects"].delete_one({"_id": project["_id"]})
    logger.info(f"Deleted project '{project['title']}' and {deleted_tasks_result.deleted_count} tasks")
    return

@project_router.post("/{id}/members/{user_email}", response_model=Project)
async def add_project_member(id: str, user_email: str, current_user: dict = Depends(get_current_user)):
    """
    Add a user as a project member by email (manager-only).

    Verifies manager privileges, checks the target user exists and isn't
    already part of the project, then adds them to the `members` array.
    Returns the project document.
    """
    project = await is_project_manager(ObjectId(id), current_user["_id"])
    user = await get_database()["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if any(member["_id"] == user["_id"] for member in project.get("members", [])):
        raise HTTPException(status_code=400, detail="User is already a member of the project")
    updated = await get_database()["projects"].find_one_and_update(
        {"_id": project["_id"]},
        {"$addToSet": {"members": {
            "_id": user["_id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "role": "member"
        }}},
        return_document=ReturnDocument.AFTER
    )
    logger.info(f"Added user '{user['first_name']} {user['last_name']}' to project '{project['title']}'")
    return updated

@project_router.delete("/{id}/members/{user_email}", response_model=Project)
async def remove_project_member(id: str, user_email: str, current_user: dict = Depends(get_current_user)):
    """
    Remove a user from the project's members list (manager-only).

    Ensures the acting user is a manager, confirms the specified email is
    currently a member, and removes them from the `members` array.
    Returns the project document.
    """
    project = await is_project_manager(ObjectId(id), current_user["_id"])
    user = await get_database()["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not any(member["email"] == user_email for member in project.get("members", [])):
        raise HTTPException(status_code=400, detail="User is not a member of the project")
    await get_database()["tasks"].update_many(
        {"project._id": project["_id"], "assigned_to._id": user["_id"]},
        {"$set": {"assigned_to": None}}
    )

    updated = await get_database()["projects"].find_one_and_update(
        {"_id": project["_id"]},
        {"$pull": {"members": {"email": user_email}}},
        return_document=ReturnDocument.AFTER
    )
    logger.info(f"Removed user '{user_email}' from project '{project['title']}' and unassigned their tasks in the project")
    return updated

@project_router.delete("/{id}/managers/{user_email}", response_model=Project)
async def remove_project_manager(id: str, user_email: str, current_user: dict = Depends(get_current_user)):
    """
    Demote a project manager to a regular member.

    Confirms the acting user is a manager, verifies the target user exists
    and is currently a manager, then moves them from `managers` to
    the `members` array.
    Returns the project document.
    """
    project = await is_project_manager(ObjectId(id), current_user["_id"])
    user = await get_database()["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any(m.get("_id") == user["_id"] and m.get("role") == "manager" for m in project.get("members", [])):
        raise HTTPException(status_code=400, detail="User is not a manager of the project")

    await get_database()["projects"].update_one(
        {"_id": project["_id"], "members._id": user["_id"]},
        {"$set": {"members.$.role": "member"}}
    )
    updated = await get_database()["projects"].find_one({"_id": project["_id"]})
    logger.info(f"Demoted user '{user_email}' to member in project '{project['title']}'")
    return updated

@project_router.post("/{id}/managers/{user_email}", response_model=Project)
async def add_project_manager(id: str, user_email: str, current_user: dict = Depends(get_current_user)):
    """
    Promote a project member to manager (manager-only).

    Ensures the target user exists and is currently a member, then moves
    them from `members` to `managers`. Returns the project document.
    """
    project = await is_project_manager(ObjectId(id), current_user["_id"])
    user = await get_database()["users"].find_one({"email": user_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if any(m.get("_id") == user["_id"] and m.get("role") == "manager" for m in project.get("members", [])):
        raise HTTPException(status_code=400, detail="User is already a manager of the project")
    if not any(m.get("_id") == user["_id"] for m in project.get("members", [])):
        raise HTTPException(status_code=400, detail="User isn't already a member of the project")

    await get_database()["projects"].update_one(
        {"_id": project["_id"], "members._id": user["_id"]},
        {"$set": {"members.$.role": "manager"}}
    )
    updated = await get_database()["projects"].find_one({"_id": project["_id"]})
    logger.info(f"Promoted user '{user['first_name']} {user['last_name']}' to manager in project '{project['title']}'")
    return updated

    
@project_router.post("/{id}/tasks/", response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(id: str, task: CreateTaskRequest, current_user: dict = Depends(get_current_user)):
    """
    Create a new task under the specified project (manager-only).

    Validates that the current user is a manager, constructs a task
    document with default fields and inserts it into the `tasks`
    collection. Returns the new task's ID.
    """
    project = await is_project_manager(ObjectId(id), current_user["_id"])

    task_doc = {
        "title": task.title,
        "description": task.description,
        "project": {
            "_id": project["_id"],
            "project_title": project["title"]
        },
        "assigned_to": None,
        "state": "NOT STARTED",
        "priority": task.priority,
        "deadline": task.deadline,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    result = await get_database()["tasks"].insert_one(task_doc)
    logger.info(f"Created task '{task.title}'")
    return CreateTaskResponse(id=str(result.inserted_id))

@project_router.patch("/{project_id}/tasks/{task_id}", response_model=Task)
async def update_task(
    project_id: str,
    task_id: str,
    update_data: TaskUpdate,
    current_user = Depends(get_current_user)
):
    """
    Update a task's fields with role-based permissions.

    - Project managers may update title, description, priority, assigned_to,
        deadline and state.
    - The assigned user may update the task's `state`, but they are not
        allowed to mark a task as `COMPLETED` (managers must do that).

    The function validates IDs, permission, and normalizes payloads
    before performing an atomic update and returning the updated task.
    """
    db = get_database()
    if not ObjectId.is_valid(task_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task ID format.")

    task = await db["tasks"].find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    
    if task["project"]["_id"] != ObjectId(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task does not belong to the specified project.")
    
    project = await db["projects"].find_one({"_id": task["project"]["_id"]})
    
    if not project:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Associated project not found.")

    is_manager = any(m.get("_id") == current_user["_id"] and m.get("role") == "manager" for m in project.get("members", []))
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

    update_fields = update_data.model_dump(exclude_unset=True)

    if 'assigned_to' in update_fields and update_fields['assigned_to'] is not None:
        at = update_fields['assigned_to']
        if isinstance(at, dict) and 'id' in at and '_id' not in at:
            at['_id'] = ObjectId(at['id']) if ObjectId.is_valid(at['id']) else at['id']
            del at['id']
        update_fields['assigned_to'] = at
    
    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request body cannot be empty.")

    update_doc = {}

    for field, value in update_fields.items():
        if field == "state":
            if is_manager:
                update_doc["state"] = value
            elif is_assigned_user:
                if value == "COMPLETED":
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only a project manager can complete a task.")
                update_doc["state"] = value
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to change this task's state.")
        
        elif field in ["title", "description", "priority", "assigned_to", "deadline"]:
            logger = logging.getLogger("inf3-projet-api")
            logger.info(f"Updating task {task_id} field '{field}' to {value}")
            if not is_manager:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Only a project manager can update the task's {field}.")
            update_doc[field] = value if not isinstance(value, BaseModel) else value.model_dump()
        else:
            pass 


    if not update_doc:
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
    """
    List all tasks for a given project the current user can access.

    Ensures the user is a member or manager of the project and returns
    all tasks referencing the project's ID.
    """
    project = await _fetch_project_for_user(id, current_user)
    tasks = await get_database()["tasks"].find({
        "project._id": project["_id"]
    }).to_list()
    return tasks

@project_router.get("/{project_id}/tasks/{task_id}", response_model=Task)
async def get_task(project_id: str, task_id: str, current_user: dict = Depends(get_current_user)):
    """
    Retrieve a single task by project and task ID for authorized users.

    Confirms the current user belongs to the project and that the task
    references the project before returning it.
    """
    project = await _fetch_project_for_user(project_id, current_user)
    task = await get_database()["tasks"].find_one({
        "_id": ObjectId(task_id),
        "project._id": project["_id"]
    })
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@project_router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(project_id: str, task_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a task from a project (manager-only).

    Validates manager privileges and that the task belongs to the project,
    then deletes the task document.
    """
    project = await is_project_manager(ObjectId(project_id), current_user["_id"])
    task = await get_database()["tasks"].find_one({
        "_id": ObjectId(task_id),
        "project._id": project["_id"]
    })
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await get_database()["tasks"].delete_one({"_id": task["_id"]})
    logger.info(f"Deleted task '{task['title']}' from project '{project['title']}'")
    return
