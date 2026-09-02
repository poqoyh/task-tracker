from fastapi import HTTPException

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.permissions.projects import (
    can_view_project,
    can_manage_project,
    can_create_project,
)


from crud_repositories.project import (
    create_project,
    get_project_by_id,
    get_projects,
    count_projects,
    update_project,
    get_project_for_update,
)

from db.models import User

from schemas.pagination import PaginatedResponse

from schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)


async def get_projects_service(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> PaginatedResponse[ProjectRead]:

    items = await get_projects(session=session, limit=limit, offset=offset)
    total = await count_projects(session=session)

    return PaginatedResponse[ProjectRead](
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_project_by_id_service(
    session: AsyncSession,
    project_id: int,
):

    project = await get_project_by_id(session=session, project_id=project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


async def get_project_service(
    session: AsyncSession,
    project_id: int,
    current_user: User,
):
    project = await get_project_by_id_service(session=session, project_id=project_id)

    if not can_view_project(current_user=current_user, project=project):
        raise HTTPException(
            status_code=403, detail="Not enough permission to view this project"
        )

    return project


async def get_project_for_update_service(
    session: AsyncSession,
    project_id: int,
):
    project = await get_project_for_update(
        session=session,
        project_id=project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


async def create_project_service(
    session: AsyncSession,
    creating_project: ProjectCreate,
    current_user: User,
):
    if not can_create_project(
        current_user=current_user, team_id=creating_project.team_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to create a project for this team",
        )

    project_data = creating_project.model_dump()

    try:
        return await create_project(
            session=session,
            project_data=project_data,
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Project with this key already exist.",
        )


async def update_project_service(
    session: AsyncSession,
    project_id: int,
    update_data: ProjectUpdate,
    current_user: User,
):

    project = await get_project_by_id_service(
        session=session,
        project_id=project_id,
    )

    if not can_manage_project(current_user=current_user, project=project):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to manage this project"
        )

    update_data = update_data.model_dump(exclude_unset=True)

    return await update_project(
        session=session,
        project=project,
        update_data=update_data,
    )
