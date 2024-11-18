from fastapi import APIRouter

from app.api.endpoints.api_composition import router as api_composition_router
from app.api.endpoints.fdw import router as fdw_router
from app.api.endpoints.shared_db import router as shared_db_router

api_router = APIRouter(prefix="/assessments")
api_router.include_router(api_composition_router, prefix="/api-composition")
api_router.include_router(fdw_router, prefix="/fdw")
api_router.include_router(shared_db_router, prefix="/shared-db")
