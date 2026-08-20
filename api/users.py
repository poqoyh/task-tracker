from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    Response,
)

from auth.dependencies import get_current_user, get_user_for_refresh_token, require_role

from auth.jwt import (
    create_access_token,
    create_refresh_token,
)

from auth.service import (
    register_user_service,
    authenticate_user_service,
    get_user_by_id_service,
    update_user_service,
    change_user_role_service,
)
from core.config import settings
from crud_repositories.user import get_all_users, get_user_profile

from db import db_helper
from db.models import User
from db.models.user import UserRole
from schemas.pagination import PaginationParams

from schemas.user import (
    UserCreate,
    UserLogin,
    UserShortRead,
    UserUpdate,
    UserProfileRead,
)

router = APIRouter(tags=["Users"])


@router.post("/register")
async def register(
    user_create: UserCreate,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await register_user_service(session=session, creating_user=user_create)


@router.post("/login")
async def login(
    response: Response,
    user_login: UserLogin,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    user = await authenticate_user_service(session, user_login)

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.auth.cookie_secure,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.auth.cookie_secure,
        samesite="lax",
    )

    return {"message": "Login successful"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "Logout successful"}


@router.post("/refresh")
async def refresh(
    response: Response,
    current_user: User = Depends(get_user_for_refresh_token),
):
    access_token = create_access_token(current_user)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.auth.cookie_secure,
        samesite="lax",
    )

    return {"message": "Token updated successfully"}


@router.get("/", response_model=list[UserShortRead])
async def get_users(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    pagination: Annotated[PaginationParams, Depends()],
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_all_users(
        session, limit=pagination.limit, offset=pagination.offset
    )


@router.get("/me", response_model=UserShortRead)
async def me(
    current_user: User = Depends(get_current_user),
    _: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TEAM_LEAD, UserRole.WORKER)
    ),
):
    return current_user


@router.get("/profile", response_model=UserProfileRead)
async def profile(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    current_user: User = Depends(get_current_user),
    _: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TEAM_LEAD, UserRole.WORKER)
    ),
):
    return await get_user_profile(
        session=session,
        user_id=current_user.id,
    )


@router.get("/{user_id}", response_model=UserShortRead)
async def get_user_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_user_by_id_service(session=session, user_id=user_id)


@router.patch("/{user_id}", response_model=UserShortRead)
async def update_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    user_update_data: UserUpdate,
    _: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TEAM_LEAD, UserRole.WORKER)
    ),
):
    return await update_user_service(
        session=session,
        user_id=user_id,
        user_update_data=user_update_data,
    )


@router.patch("/{user_id}/role", response_model=UserShortRead)
async def change_user_role(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    new_role: UserRole,
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    return await change_user_role_service(
        session=session,
        user_id=user_id,
        new_role=new_role,
    )
