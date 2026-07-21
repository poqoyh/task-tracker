from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.task import get_task_by_id
from db.models import Task


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
