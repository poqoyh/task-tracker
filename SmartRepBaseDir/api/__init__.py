from core.config import settings

from fastapi import APIRouter

from .users import router as users_router
from .skills import router as skills_router
from .users_skills import router as users_skills_router
from .teams import router as team_router

router = APIRouter()

router.include_router(users_router, prefix=settings.api.users)
router.include_router(skills_router, prefix=settings.api.skills)
router.include_router(users_skills_router, prefix=settings.api.user_skills)
router.include_router(team_router, prefix=settings.api.team)
