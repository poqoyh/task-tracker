from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import User, UserSkill
from db.models.user import UserRole
from schemas.user import UserCreate


async def create_user(
    session: AsyncSession,
    creating_user: UserCreate,
    hashed_password: str,
) -> User:

    user_data = creating_user.model_dump()

    user_data.pop("password")
    user_data["hashed_password"] = hashed_password

    user = User(**user_data)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_all_users(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> list[User]:

    stmt = select(User).order_by(User.id).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return result.all()


async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()

    return user


async def get_user_by_id_with_team(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    stmt = select(User).where(User.id == user_id).options(selectinload(User.team))

    result = await session.scalars(stmt)

    return result.one_or_none()


async def get_user_by_id_with_skills(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.user_skills).selectinload(UserSkill.skill))
    )

    result = await session.scalars(stmt)

    return result.one_or_none()


async def get_user_profile(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.user_skills).selectinload(UserSkill.skill),
            selectinload(User.team),
            selectinload(User.tasks),
        )
    )

    result = await session.scalars(stmt)

    return result.one_or_none()


async def get_user_by_identifier(
    identifier: str,
    session: AsyncSession,
) -> User | None:
    field = User.email if "@" in identifier else User.username

    result = await session.execute(select(User).where(field == identifier))

    user = result.scalar_one_or_none()

    return user


async def update_user(
    session: AsyncSession,
    user: User,
    update_data: dict,
) -> User:
    for field, value in update_data.items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)

    return user


async def update_user_role(
    session: AsyncSession,
    user: User,
    new_role: UserRole,
) -> User:

    user.role = new_role

    await session.commit()
    await session.refresh(user)

    return user
