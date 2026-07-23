from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.user import (
    create_user,
    get_user_by_identifier,
    get_user_by_id,
    update_user,
)

from auth.hashing import hash_password, validate_password
from db.models import User

from schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
)


async def register_user_service(
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


async def authenticate_user_service(
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

    return user



async def update_user_service(
    session: AsyncSession,
    user_id: int,
    user_update_data: UserUpdate,
):
    user = await get_user_by_id_service(session=session, user_id=user_id)

    update_data = user_update_data.model_dump(exclude_unset=True)

    return await update_user(
        session=session,
        user=user,
        update_data=update_data,
    )
