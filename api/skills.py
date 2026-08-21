from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from auth.dependencies import require_role
from db import db_helper
from db.models.user import UserRole, User
from schemas.pagination import PaginationParams, PaginatedResponse

from schemas.skill import (
    SkillCreate,
    SkillShortRead,
    SkillUpdate,
)

from crud_repositories.skill import (
    create_skill,
)

from service.skills import (
    delete_skill_service,
    get_skill_by_id_service,
    get_skill_by_name_service,
    update_skill_service,
    get_skills_service,
)

router = APIRouter(tags=["Skills"])


@router.post("/", response_model=SkillShortRead)
async def skill_create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    creating_skill: SkillCreate,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await create_skill(session=session, creating_skill=creating_skill)


@router.get("/", response_model=PaginatedResponse[SkillShortRead])
async def get_all_skills(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    pagination: Annotated[PaginationParams, Depends()],
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_skills_service(
        session, limit=pagination.limit, offset=pagination.offset
    )


@router.get("/{skill_id}/", response_model=SkillShortRead)
async def get_skill_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    skill_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_skill_by_id_service(session=session, skill_id=skill_id)


@router.get("/by-name/{skill_name}", response_model=SkillShortRead)
async def get_skill_by_name(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    skill_name: str,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_skill_by_name_service(session=session, skill_name=skill_name)


@router.patch("/{skill_id}", response_model=SkillShortRead)
async def update_skill(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    skill_id: int,
    update_data: SkillUpdate,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await update_skill_service(
        skill_id=skill_id,
        update_data=update_data,
        session=session,
    )


@router.delete("/{skill_id}")
async def delete_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    skill_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    await delete_skill_service(
        skill_id=skill_id,
        session=session,
    )
    return {"message": "Skill deleted successfully."}
