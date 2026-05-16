from fastapi import APIRouter

from .sos import router as sos_router
from .ai_safety import router as ai_safety_router
from .crime import router as crime_router
from .routes import router as routing_router

router = APIRouter()

# Combine all available sub-routers
router.include_router(sos_router)
router.include_router(ai_safety_router)
router.include_router(crime_router)
router.include_router(routing_router)
