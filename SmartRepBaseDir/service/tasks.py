from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.task import get_task_by_id, update_task
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
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    update_data = task_update.model_dump(exclude_unset=True)

    return await update_task(
        session=session,
        task=task,
        task_update=update_data,
    )
