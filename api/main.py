from fastapi import FastAPI
import logging
from routes.auth import auth_router
from db import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes.projects import project_router
from routes.users import user_router

logging.basicConfig(level=logging.INFO)

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
app.router.include_router(user_router)
