from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from auth.permissions.user_skills import can_manage_user_skills
from crud_repositories.user import get_user_by_id_with_skills
from crud_repositories.user_skill import (
    create_skill_for_user,
    get_user_skill,
    delete_user_skill,
    update_experience,
    get_users_skills,
)
from db.models import User

from schemas.user_skill import UserSkillCreate

from service.skills import get_skill_by_id_service
from auth.service import get_user_by_id_service


async def get_user_skills_service(
    session: AsyncSession,
    user_id: int,
    current_user: User,
):
    target_user = await get_user_by_id_service(session=session, user_id=user_id)

    if not can_manage_user_skills(current_user=current_user, target_user=target_user):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to view this user's skills"
        )

    return await get_users_skills(session=session, user_id=user_id)


async def assign_skill_to_user_service(
    session: AsyncSession,
    user_id: int,
    data: UserSkillCreate,
    current_user: User,
):
    target_user = await get_user_by_id_service(
        session=session,
        user_id=user_id,
    )

    if not can_manage_user_skills(current_user=current_user, target_user=target_user):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to manage this user's skills",
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

    await create_skill_for_user(
        session=session,
        skill_id=data.skill_id,
        user_id=user_id,
        experience_months=data.experience_months,
    )

    return await get_user_by_id_with_skills(session=session, user_id=user_id)


async def update_experience_months_service(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
    new_experience: int,
    current_user: User,
):
    target_user = await get_user_by_id_service(session=session, user_id=user_id)

    if not can_manage_user_skills(current_user=current_user, target_user=target_user):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to manage this user's skills",
        )

    await get_skill_by_id_service(session=session, skill_id=skill_id)

    user_skill = await get_user_skill(
        session=session, user_id=user_id, skill_id=skill_id
    )
    if user_skill is None:
        raise HTTPException(
            status_code=404,
            detail="User doesn't have this skill.",
        )

    await update_experience(
        session=session,
        user_skill=user_skill,
        new_experience=new_experience,
    )

    return await get_user_by_id_with_skills(session=session, user_id=user_id)


async def delete_user_skill_service(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
    current_user: User,
):
    target_user = await get_user_by_id_service(session=session, user_id=user_id)

    if not can_manage_user_skills(current_user=current_user, target_user=target_user):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to manage this user's skills",
        )

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
