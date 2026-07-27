from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.service import get_user_by_id_service
from crud_repositories.task import (
    get_task_by_id,
    update_task,
    assign_task_to_user,
    unassign_task,
)
from db.models import Task
from schemas.tasks import TaskUpdate


async def get_task_by_id_service(
    session: AsyncSession,
    task_id: int,
) -> Task:
    task = await get_task_by_id(
        session=session,
        task_id=task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    return task


async def update_task_service(
    session: AsyncSession,
    task_id: int,
    task_update: TaskUpdate,
):
    task = await get_task_by_id_service(
        session=session,
        task_id=task_id,
    )

    update_data = task_update.model_dump(exclude_unset=True)

    return await update_task(
        session=session,
        task=task,
        task_update=update_data,
    )


async def assign_task_to_user_service(
    session: AsyncSession,
    task_id: int,
    user_id: int,
):
    task = await get_task_by_id_service(
        session=session,
        task_id=task_id,
    )

    if task.user_id is not None:
        raise HTTPException(
            status_code=409,
            detail="Task already assigned.",
        )

    await get_user_by_id_service(
        session=session,
        user_id=user_id,
    )

    return await assign_task_to_user(
        session=session,
        task=task,
        user_id=user_id,
    )


async def unassign_task_from_user_service(
    session: AsyncSession,
    task_id: int,
):
    task = await get_task_by_id_service(
        session=session,
        task_id=task_id,
    )

    return await unassign_task(session=session, task=task)
