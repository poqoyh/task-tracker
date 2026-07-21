from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Task
from schemas.tasks import TaskCreate


async def create_task(
    session: AsyncSession,
    creating_task: TaskCreate,
) -> Task:

    task = Task(**creating_task.model_dump())

    session.add(task)

    await session.commit()
    await session.refresh(task)

    return task
