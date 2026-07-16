from core.config import settings

from fastapi import APIRouter

from .users import router as users_router
from .skills import router as skills_router

router = APIRouter()

router.include_router(users_router, prefix=settings.api.users)
router.include_router(skills_router, prefix=settings.api.skills)
