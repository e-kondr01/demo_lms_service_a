from fastapi import APIRouter

from app.api.endpoints.student_progress import router as student_progress_router

api_router = APIRouter()
api_router.include_router(student_progress_router, prefix="/student-progresses")
