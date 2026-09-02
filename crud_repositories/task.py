from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    limit: int,
    offset: int,
) -> list[Task]:

    stmt = select(Task).order_by(Task.created_at).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return result.all()


async def count_tasks(session: AsyncSession) -> int:
    result = await session.scalar(select(func.count()).select_from(Task))

    return result or 0


async def get_users_tasks(
    session: AsyncSession,
    user_id: int,
) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at)

    result = await session.scalars(stmt)
    return result.all()


async def get_task_by_id(
    session: AsyncSession,
    task_id: int,
) -> Task | None:

    stmt = (
        select(Task)
        .options(selectinload(Task.user), selectinload(Task.project))
        .where(Task.id == task_id)
    )

    task = await session.scalars(stmt)
    return task.one_or_none()


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


async def assign_task_to_user(
    session: AsyncSession,
    task: Task,
    user_id: int,
) -> Task:
    task.user_id = user_id

    await session.commit()
    await session.refresh(task)

    return task


async def unassign_task(
    session: AsyncSession,
    task: Task,
) -> Task:
    task.user_id = None

    await session.commit()
    await session.refresh(task)

    return task
