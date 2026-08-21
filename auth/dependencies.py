from typing import Annotated

import jwt
from fastapi import Request, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from db import db_helper
from db.models import User
from db.models.user import UserRole

from .jwt import decode_jwt


async def get_user_by_token(
    request: Request,
    session: AsyncSession,
    cookie_name: str,
    expected_type: str,
) -> User:
    token = request.cookies.get(cookie_name)

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    try:
        payload = decode_jwt(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    if payload.get("type") != expected_type:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    user = await session.get(User, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    return user


async def get_current_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    request: Request,
) -> User:
    return await get_user_by_token(
        request=request,
        session=session,
        cookie_name="access_token",
        expected_type="access",
    )


async def get_user_for_refresh_token(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
) -> User:
    return await get_user_by_token(
        request=request,
        session=session,
        cookie_name="refresh_token",
        expected_type="refresh",
    )


def require_role(*roles: UserRole):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
            )
        return current_user

    return checker
