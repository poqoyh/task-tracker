from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Skill
from schemas.skill import SkillCreate


async def create_skill(
    session: AsyncSession,
    creating_skill: SkillCreate,
) -> Skill:

    skill_data = creating_skill.model_dump()

    skill = Skill(**skill_data)

    session.add(skill)
    await session.commit()
    await session.refresh(skill)
    return skill


async def get_skill_by_id(
    session: AsyncSession,
    skill_id: int,
) -> Skill | None:

    stmt = select(Skill).where(Skill.id == skill_id)

    result = await session.scalars(stmt)
    result = result.one_or_none()

    return result


async def get_skill_by_name(
    session: AsyncSession,
    skill_name: str,
) -> Skill | None:
    stmt = select(Skill).where(Skill.name == skill_name)

    result = await session.scalars(stmt)
    result = result.one_or_none()

    return result


async def get_skills(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> list[Skill]:

    stmt = select(Skill).order_by(Skill.id).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return result.all()


async def count_skills(session: AsyncSession) -> int:
    result = await session.scalar(select(func.count()).select_from(Skill))

    return result or 0


async def update_skill(
    session: AsyncSession,
    skill: Skill,
    update_data: dict,
):
    for field, value in update_data.items():
        setattr(skill, field, value)

    await session.commit()
    await session.refresh(skill)

    return skill


async def delete_skill(
    session: AsyncSession,
    skill: Skill,
):
    await session.delete(skill)
    await session.commit()
