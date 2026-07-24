from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from db import db_helper
from db.models import User
from schemas.user_skill import UserSkillCreate, UserSkillRead

from service.user_skills import (
    assign_skill_to_user_service,
    delete_user_skill_service,
    update_experience_months_service,
)

from crud_repositories.user_skill import get_users_skills

router = APIRouter(tags=["UsersSkills"])


@router.get("/me/skills", response_model=list[UserSkillRead])
async def get_my_skills(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await get_users_skills(session=session, user_id=int(current_user.id))


@router.get("/{user_id}/skills/", response_model=list[UserSkillRead])
async def get_user_skills(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
):
    return await get_users_skills(session=session, user_id=user_id)


@router.post("/{user_id}/skills", response_model=UserSkillRead)
async def add_skill_to_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    data: UserSkillCreate,
):
    return await assign_skill_to_user_service(
        session=session, user_id=user_id, data=data
    )


@router.patch("/{user_id}/skills/{skill_id}")
async def update_user_skill(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user_id: int,
    new_experience: int,
    skill_id: int,
):
    return await update_experience_months_service(
        session=session,
        user_id=user_id,
        new_experience=new_experience,
        skill_id=skill_id,
    )


@router.delete("/{user_id}/skills/{skill_id}")
async def delete_user_skill(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    skill_id: int,
):
    await delete_user_skill_service(session=session, user_id=user_id, skill_id=skill_id)
    return {"message": "Skill deleted successfully."}
