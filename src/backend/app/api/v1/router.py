from fastapi import APIRouter

from app.api.v1.endpoints.assets import router as assets_router
from app.api.v1.endpoints.curriculum import router as curriculum_router
from app.api.v1.endpoints.exams import router as exams_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.items import router as items_router
from app.api.v1.endpoints.omr_read import router as omr_read_router

api_router = APIRouter()
api_router.include_router(curriculum_router)
api_router.include_router(assets_router)
api_router.include_router(exams_router)
api_router.include_router(health_router)
api_router.include_router(items_router)
api_router.include_router(omr_read_router)
