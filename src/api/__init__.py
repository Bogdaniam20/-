from fastapi import APIRouter

from src.api.Task import router as task_router

main_router = APIRouter()

main_router.include_router(task_router)