from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.user_skill import (
    create_skill_for_user,
    get_user_skill,
    delete_user_skill,
    update_experience,
    skill_has_user,
)
from schemas.user_skill import UserSkillCreate

from service.skills import get_skill_by_id_service
from auth.service import get_user_by_id_service


async def assign_skill_to_user_service(
    session: AsyncSession,
    user_id: int,
    data: UserSkillCreate,
):
    await get_user_by_id_service(
        session=session,
        user_id=user_id,
    )
    await get_skill_by_id_service(
        session=session,
        skill_id=data.skill_id,
    )

    if await get_user_skill(
        session=session,
        user_id=user_id,
        skill_id=data.skill_id,
    ):
        raise HTTPException(
            status_code=409,
            detail="User already has this skill",
        )

    return await create_skill_for_user(
        session=session,
        skill_id=data.skill_id,
        user_id=user_id,
        experience_months=data.experience_months,
    )


async def update_experience_months_service(
    session: AsyncSession,
    user_id: int,
    new_experience: int,
    skill_id: int,
):
    await get_user_by_id_service(session=session, user_id=user_id)

    await get_skill_by_id_service(session=session, skill_id=skill_id)

    user_skill = await get_user_skill(
        session=session, user_id=user_id, skill_id=skill_id
    )
    if user_skill is None:
        raise HTTPException(
            status_code=404,
            detail="User haven't this skill.",
        )
    return await update_experience(
        session=session,
        user_skill=user_skill,
        new_experience=new_experience,
    )


async def delete_user_skill_service(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
):
    skill = await get_user_skill(
        session=session,
        user_id=user_id,
        skill_id=skill_id,
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="skill not found.",
        )

    await delete_user_skill(session=session, skill=skill)
