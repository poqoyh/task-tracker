from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
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


async def get_user_by_identifier(
    identifier: str,
    session: AsyncSession,
) -> User | None:
    field = User.email if "@" in identifier else User.username

    result = await session.execute(select(User).where(field == identifier))

    user = result.scalar_one_or_none()

    return user
