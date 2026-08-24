from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.user import (
    create_user,
    get_user_by_identifier,
    get_user_by_id,
    update_user,
    update_user_role,
    count_users,
    get_all_users,
)

from auth.hashing import hash_password, validate_password
from auth.premissions import can_update_user


from db.models.user import UserRole, User
from schemas.pagination import PaginatedResponse

from schemas.user import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserShortRead,
)


async def register_user_service(
    session: AsyncSession,
    creating_user: UserCreate,
):
    hashed_password = hash_password(creating_user.password)

    user = await create_user(
        session=session,
        hashed_password=hashed_password,
        creating_user=creating_user,
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
    user = await get_user_by_identifier(
        session=session, identifier=user_login.identifier
    )

    if not user or not validate_password(
        user_login.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    return user


async def get_users_service(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> PaginatedResponse[UserShortRead]:
    items = await get_all_users(session=session, limit=limit, offset=offset)
    total = await count_users(session)

    return PaginatedResponse[UserShortRead](
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


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
    current_user: User,
):
    target_user = await get_user_by_id_service(session=session, user_id=user_id)

    if not can_update_user(current_user=current_user, target_user=target_user):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to update this user"
        )

    update_data = user_update_data.model_dump(exclude_unset=True)

    try:
        return await update_user(
            session=session,
            user=target_user,
            update_data=update_data,
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email or username already taken",
        )


async def change_user_role_service(
    session: AsyncSession,
    user_id: int,
    new_role: UserRole,
):
    user = await get_user_by_id_service(session=session, user_id=user_id)

    return await update_user_role(
        session=session,
        user=user,
        new_role=new_role,
    )
