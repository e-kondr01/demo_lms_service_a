from fastapi import APIRouter

from app.api.endpoints.assessment import router as assessment_router
from app.api.endpoints.fdwdemo import router as fdwdemo_router

api_router = APIRouter()
api_router.include_router(assessment_router, prefix="/assessments")
api_router.include_router(fdwdemo_router, prefix="/fdwdemos")
