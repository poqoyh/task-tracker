from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.skill import (
    get_skill_by_id,
    change_skill_name,
    delete_skill,
    get_skill_by_name,
)


async def update_skill_name_service(
    skill_id: int,
    new_skill_name: str,
    session: AsyncSession,
):
    skill = await get_skill_by_id(
        session,
        skill_id,
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    return await change_skill_name(
        session=session, skill=skill, new_skill_name=new_skill_name
    )


async def delete_skill_service(
    skill_id: int,
    session: AsyncSession,
):
    skill = await get_skill_by_id(
        session,
        skill_id,
    )

    if skill is None:
        raise HTTPException(
            status_code=404,
            detail="Skill not found",
        )

    await delete_skill(session, skill)


async def get_skill_by_id_service(
    skill_id: int,
    session: AsyncSession,
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
    skill_name: str,
    session: AsyncSession,
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
