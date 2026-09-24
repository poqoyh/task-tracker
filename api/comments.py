from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from auth.dependencies import get_current_user

from db import db_helper
from db.models import User

from schemas.pagination import PaginationParams, PaginatedResponse
from schemas.comment import CommentRead, CommentCreate, CommentUpdate

from service.comment import (
    create_comment_service,
    get_task_comments_service,
    get_comment_by_id_service,
    update_comment_service,
    delete_comment_service,
)

router = APIRouter(tags=["Comments"])


@router.post("/tasks/{task_id}/comments", response_model=CommentRead)
async def create_comment(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
):
    return await create_comment_service(
        session=session,
        task_id=task_id,
        comment_data=comment_data,
        current_user=current_user,
    )


@router.get("/tasks/{task_id}/comments", response_model=PaginatedResponse[CommentRead])
async def get_task_comments(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
    pagination: Annotated[PaginationParams, Depends()],
    current_user: User = Depends(get_current_user),
):
    return await get_task_comments_service(
        session=session,
        task_id=task_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/comments/{comment_id}", response_model=CommentRead)
async def get_comment_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    comment_id: int,
    current_user: User = Depends(get_current_user),
):
    return await get_comment_by_id_service(session=session, comment_id=comment_id)


@router.patch("/comments/{comment_id}", response_model=CommentRead)
async def update_comment(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_user),
):
    return await update_comment_service(
        session=session,
        comment_id=comment_id,
        comment_update=comment_update,
        current_user=current_user,
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    comment_id: int,
    current_user: User = Depends(get_current_user),
):
    await delete_comment_service(
        session=session,
        comment_id=comment_id,
        current_user=current_user,
    )
