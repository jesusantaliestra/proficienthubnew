"""
Public API v1 - Main Router
All public API endpoints are versioned under /api/v1/
"""
from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["Public API v1"])

# Import and include all v1 routers
from .institutions import router as institutions_router
from .students import router as students_router
from .exams import router as exams_router
from .analytics import router as analytics_router
from .billing import router as billing_router
from .webhooks import router as webhooks_router

router.include_router(institutions_router)
router.include_router(students_router)
router.include_router(exams_router)
router.include_router(analytics_router)
router.include_router(billing_router)
router.include_router(webhooks_router)
