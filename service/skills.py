from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.skill import (
    get_skill_by_id,
    delete_skill,
    get_skill_by_name,
    update_skill,
    get_skills,
    count_skills,
    create_skill,
)
from crud_repositories.user_skill import skill_has_user
from schemas.pagination import PaginatedResponse

from schemas.skill import SkillUpdate, SkillShortRead, SkillCreate


async def create_skill_service(
    session: AsyncSession,
    creating_skill: SkillCreate,
):
    try:
        return await create_skill(session=session, creating_skill=creating_skill)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Skill with this name is already create"
        )


async def get_skills_service(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> PaginatedResponse[SkillShortRead]:
    items = await get_skills(session=session, limit=limit, offset=offset)
    total = await count_skills(session=session)

    return PaginatedResponse[SkillShortRead](
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_skill_by_id_service(
    session: AsyncSession,
    skill_id: int,
):
    skill = await get_skill_by_id(
        session=session,
        skill_id=skill_id,
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return skill


async def get_skill_by_name_service(
    session: AsyncSession,
    skill_name: str,
):
    skill = await get_skill_by_name(
        session=session,
        skill_name=skill_name,
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return skill


async def update_skill_service(
    session: AsyncSession,
    skill_id: int,
    update_data: SkillUpdate,
):
    skill = await get_skill_by_id_service(skill_id=skill_id, session=session)

    data = update_data.model_dump(exclude_unset=True)

    try:
        return await update_skill(session=session, skill=skill, update_data=data)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="Skill with this name is already create"
        )


async def delete_skill_service(
    session: AsyncSession,
    skill_id: int,
):
    if await skill_has_user(skill_id=skill_id, session=session):
        raise HTTPException(
            status_code=409,
            detail="Skill has a users",
        )

    skill = await get_skill_by_id_service(skill_id=skill_id, session=session)

    await delete_skill(session, skill)
