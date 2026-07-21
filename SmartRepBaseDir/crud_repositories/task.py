from sqlalchemy import select
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


async def get_tasks(
    session: AsyncSession,
) -> list[Task] | list[None]:

    stmt = select(Task).order_by(Task.created_at)

    result = await session.scalars(stmt)

    return result.all()


async def get_task_by_id(
    session: AsyncSession,
    task_id: int,
) -> Task | None:

    stmt = select(Task).where(Task.id == task_id)

    task = await session.execute(stmt)
    return task.scalar_one_or_none()


async def update_task(
    session: AsyncSession,
    task: Task,
    task_update: dict,
) -> Task:

    for field, value in task_update.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)

    return task
