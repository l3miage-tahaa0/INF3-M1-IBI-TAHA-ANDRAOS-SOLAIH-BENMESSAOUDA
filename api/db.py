import os
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from pymongo import ASCENDING


client = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client.project
    await db["users"].create_index([("email", ASCENDING)], unique=True)
    await db["tasks"].create_index([("project._id", ASCENDING)])
    await db["tasks"].create_index([("project._id", ASCENDING), ("state", ASCENDING), ("priority", ASCENDING)])
    await db["tasks"].create_index([("assigned_to._id", ASCENDING), ("state", ASCENDING)])
    await db["projects"].create_index([("members._id", ASCENDING)]) 
    await db["projects"].create_index([("members._id", ASCENDING), ("members.role", ASCENDING)])

async def close_mongo_connection():
    global client
    client.close()

def get_database():
    return db