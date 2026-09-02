from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Project


async def create_project(
    session: AsyncSession,
    project_data: dict,
) -> Project:

    project = Project(**project_data)

    session.add(project)

    await session.commit()
    await session.refresh(project)

    return project


async def get_project_by_id(
    session: AsyncSession,
    project_id: int,
) -> Project | None:

    stmt = select(Project).where(Project.id == project_id)

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def get_projects(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> list[Project]:

    stmt = select(Project).order_by(Project.name).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return result.all()


async def count_projects(session: AsyncSession) -> int:
    result = await session.scalar(select(func.count()).select_from(Project))

    return result or 0


async def get_project_for_update(
    session: AsyncSession,
    project_id: int,
) -> Project | None:

    stmt = select(Project).where(Project.id == project_id).with_for_update()

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def update_project(
    session: AsyncSession,
    project: Project,
    update_data: dict,
) -> Project:

    for field, value in update_data.items():
        setattr(project, field, value)

    await session.commit()
    await session.refresh(project)

    return project
