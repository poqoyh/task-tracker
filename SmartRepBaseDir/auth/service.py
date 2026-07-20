from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.user import (
    create_user,
    get_user_by_identifier,
    get_user_by_id,
)

from auth.hashing import hash_password, validate_password

from schemas.user import (
    UserCreate,
    UserLogin,
)


async def register_user(
    session: AsyncSession,
    creating_user: UserCreate,
):
    hashed_password = hash_password(creating_user.password)

    user = await create_user(
        session=session,
        creating_user=creating_user,
        hashed_password=hashed_password,
    )

    return {
        "message": "User created successfully",
        "username": user.username,
        "email": user.email,
    }


async def authenticate_user(
    session: AsyncSession,
    user_login: UserLogin,
):
    user = await get_user_by_identifier(user_login.identifier, session)

    if not user or not validate_password(
        user_login.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    return user


async def get_user_by_id_service(
    session: AsyncSession,
    user_id: int,
):
    user = await get_user_by_id(
        session=session,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
