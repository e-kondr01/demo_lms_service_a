from fastapi import APIRouter

from app.api.endpoints.assessment import router as assessment_router

api_router = APIRouter()
api_router.include_router(assessment_router, prefix="/assessments")
