from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from auth.permissions.comments import can_create_comment, can_manage_comment
from crud_repositories.comment import (
    create_comment,
    get_comments_by_task,
    count_comments_by_task,
    get_comment_by_id,
    update_comment,
    delete_comment,
)
from crud_repositories.task import get_task_by_id
from db.models import User
from schemas.comment import CommentCreate, CommentUpdate
from schemas.pagination import PaginatedResponse


async def create_comment_service(
    session: AsyncSession,
    task_id: int,
    comment_data: CommentCreate,
    current_user: User,
):
    task = await get_task_by_id(session=session, task_id=task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    if not can_create_comment(
        current_user=current_user,
        task_user_id=task.user_id,
        task_team_id=task.project.team_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to create comment on this task",
        )

    return await create_comment(
        session=session,
        comment_data=comment_data,
        task=task,
        user_id=current_user.id,
    )


async def get_task_comments_service(
    session: AsyncSession,
    task_id: int,
    limit: int,
    offset: int,
) -> PaginatedResponse:
    task = await get_task_by_id(session=session, task_id=task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    items = await get_comments_by_task(
        session=session,
        task_id=task_id,
        limit=limit,
        offset=offset,
    )
    total = await count_comments_by_task(session=session, task_id=task_id)

    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_comment_by_id_service(
    session: AsyncSession,
    comment_id: int,
):
    comment = await get_comment_by_id(session=session, comment_id=comment_id)

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found.",
        )

    return comment


async def update_comment_service(
    session: AsyncSession,
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: User,
):
    comment = await get_comment_by_id_service(session=session, comment_id=comment_id)

    if not can_manage_comment(current_user=current_user, comment=comment):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update this comment",
        )

    update_data = comment_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields to update",
        )

    update_data["edited_at"] = func.now()

    return await update_comment(
        session=session,
        comment=comment,
        comment_update=update_data,
    )


async def delete_comment_service(
    session: AsyncSession,
    comment_id: int,
    current_user: User,
):
    comment = await get_comment_by_id_service(session=session, comment_id=comment_id)

    if not can_manage_comment(current_user=current_user, comment=comment):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to delete this comment",
        )

    await delete_comment(session=session, comment=comment)
