from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    Response,
)

from auth.dependencies import get_current_user, get_user_for_refresh_token

from auth.jwt import (
    create_access_token,
    create_refresh_token,
)

from auth.service import (
    register_user,
    authenticate_user,
)

from db import db_helper
from db.models import User

from schemas.user import (
    UserCreate,
    UserLogin,
    UserShortRead,
)

router = APIRouter(tags=["Users"])


@router.post("/register/")
async def register(
    user_create: UserCreate,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await register_user(
        session=session,
        creating_user=user_create,
    )


@router.post("/login/")
async def login(
    response: Response,
    user_login: UserLogin,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    user = await authenticate_user(session, user_login)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True if using HTTPS
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True if using HTTPS
        samesite="lax",
    )

    return {"message": "Login successful"}


@router.post("/logout/")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "Logout successful"}


@router.get("/me/", response_model=UserShortRead)
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/refresh/")
async def refresh(
    response: Response,
    current_user: User = Depends(get_user_for_refresh_token),
):
    access_token = create_access_token(current_user)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"message": "Token updated successfully"}
