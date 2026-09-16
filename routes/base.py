from fastapi import FastAPI, APIRouter
import os


base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)

@base_router.get("/")
async def welcome():
    app_name = os.getenv("APP_NAME", "Rag-Project")
    app_version = os.getenv("APP_VERSION", "0.1")
    return {
        "message": "Welcome to the Rag-Project API!",
        "app_name": app_name,
        "app_version": app_version
    }
