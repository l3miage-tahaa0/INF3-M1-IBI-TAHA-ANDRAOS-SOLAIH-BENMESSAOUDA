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

async def close_mongo_connection():
    global client
    client.close()

def get_database():
    return db