from fastapi import APIRouter

from app.api.v1.endpoints.ai_assistant import router as ai_assistant_router
from app.api.v1.endpoints.anonymous_exams import router as anonymous_exams_router
from app.api.v1.endpoints.assets import router as assets_router
from app.api.v1.endpoints.curriculum import router as curriculum_router
from app.api.v1.endpoints.exams import router as exams_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.items import router as items_router
from app.api.v1.endpoints.omr_read import router as omr_read_router
from app.api.v1.endpoints.students import router as students_router
from app.api.v1.endpoints.student_portal import router as student_portal_router

api_router = APIRouter()
api_router.include_router(ai_assistant_router)
api_router.include_router(anonymous_exams_router)
api_router.include_router(curriculum_router)
api_router.include_router(assets_router)
api_router.include_router(exams_router)
api_router.include_router(health_router)
api_router.include_router(items_router)
api_router.include_router(omr_read_router)
api_router.include_router(students_router)
api_router.include_router(student_portal_router)
