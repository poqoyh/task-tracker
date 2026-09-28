from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Comment, Task, Project
from schemas.comment import CommentCreate


async def create_comment(
    session: AsyncSession,
    comment_data: CommentCreate,
    task: Task,
    user_id: int,
) -> Comment:
    comment = Comment(
        **comment_data.model_dump(),
        task_id=task.id,
        user_id=user_id,
    )

    session.add(comment)
    await session.commit()

    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.task)
            .selectinload(Task.project)
            .selectinload(Project.team),
            selectinload(Comment.user),
        )
        .where(Comment.id == comment.id)
    )

    result = await session.scalars(stmt)
    return result.one()


async def get_comments_by_task(
    session: AsyncSession,
    task_id: int,
    limit: int,
    offset: int,
) -> list[Comment]:
    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.task)
            .selectinload(Task.project)
            .selectinload(Project.team),
            selectinload(Comment.user),
        )
        .where(Comment.task_id == task_id)
        .order_by(Comment.created_at)
        .limit(limit)
        .offset(offset)
    )

    result = await session.scalars(stmt)
    return result.all()


async def count_comments_by_task(
    session: AsyncSession,
    task_id: int,
) -> int:
    result = await session.scalar(
        select(func.count()).select_from(Comment).where(Comment.task_id == task_id)
    )
    return result or 0


async def get_comment_by_id(
    session: AsyncSession,
    comment_id: int,
) -> Comment | None:
    stmt = (
        select(Comment)
        .options(
            selectinload(Comment.task)
            .selectinload(Task.project)
            .selectinload(Project.team),
            selectinload(Comment.user),
        )
        .where(Comment.id == comment_id)
    )

    comment = await session.scalars(stmt)
    return comment.one_or_none()


async def update_comment(
    session: AsyncSession,
    comment: Comment,
    comment_update: dict,
) -> Comment:
    for field, value in comment_update.items():
        setattr(comment, field, value)

    await session.commit()
    await session.refresh(comment)

    return comment


async def delete_comment(
    session: AsyncSession,
    comment: Comment,
) -> None:
    await session.delete(comment)
    await session.commit()
