from core.config import settings

from fastapi import APIRouter

from .users import router as users_router
from .skills import router as skills_router
from .users_skills import router as users_skills_router
from .teams import router as teams_router
from .tasks import router as tasks_router

router = APIRouter()

router.include_router(users_router, prefix=settings.api.users)
router.include_router(skills_router, prefix=settings.api.skills)
router.include_router(users_skills_router, prefix=settings.api.users_skills)
router.include_router(teams_router, prefix=settings.api.teams)
router.include_router(tasks_router, prefix=settings.api.tasks)
