from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import UserSkill


async def create_skill_for_user(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
    experience_months: int,
) -> UserSkill:

    user_skill = UserSkill(
        user_id=user_id,
        skill_id=skill_id,
        experience_months=experience_months,
    )

    session.add(user_skill)
    await session.commit()
    await session.refresh(user_skill)
    return user_skill


async def get_user_skill(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
) -> UserSkill | None:

    stmt = select(UserSkill).where(
        UserSkill.user_id == user_id,
        UserSkill.skill_id == skill_id,
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def get_users_skills(
    session: AsyncSession,
    user_id: int,
) -> list[UserSkill]:

    stmt = (
        select(UserSkill)
        .where(UserSkill.user_id == user_id)
        .options(selectinload(UserSkill.skill))
    )

    result = await session.scalars(stmt)

    return result.all()


async def skill_has_user(
    session: AsyncSession,
    skill_id: int,
):
    stmt = select(UserSkill).where(UserSkill.skill_id == skill_id).limit(1)

    result = await session.scalars(stmt)

    return result.first() is not None


async def update_experience(
    session: AsyncSession,
    user_skill: UserSkill,
    new_experience: int,
):
    user_skill.experience_months = new_experience

    await session.commit()
    await session.refresh(user_skill)

    return user_skill


async def delete_user_skill(
    session: AsyncSession,
    skill: UserSkill,
):
    await session.delete(skill)
    await session.commit()
