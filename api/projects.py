from typing import Annotated

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_role

from db import db_helper
from db.models import User
from db.models.user import UserRole

from schemas.pagination import PaginationParams, PaginatedResponse
from schemas.project import ProjectCreate, ProjectRead, ProjectUpdate


from service.projects import (
    get_projects_service,
    get_project_service,
    create_project_service,
    update_project_service,
)

router = APIRouter(tags=["Projects"])


@router.post("/", response_model=ProjectRead)
async def create_project(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    creating_project: ProjectCreate,
    current_user: User = Depends(get_current_user),
):

    return await create_project_service(
        session=session,
        creating_project=creating_project,
        current_user=current_user,
    )


@router.get("/", response_model=PaginatedResponse[ProjectRead])
async def get_all_projects(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    pagination: Annotated[PaginationParams, Depends()],
    _: User = Depends(require_role(UserRole.ADMIN)),
):

    return await get_projects_service(
        session=session, limit=pagination.limit, offset=pagination.offset
    )


@router.get("/{project_id}/", response_model=ProjectRead)
async def get_project(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    project_id: int,
    current_user: User = Depends(get_current_user),
):

    return await get_project_service(
        session=session,
        project_id=project_id,
        current_user=current_user,
    )


@router.patch("/{project_id}/", response_model=ProjectRead)
async def update_project(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    project_id: int,
    update_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
):

    return await update_project_service(
        session=session,
        project_id=project_id,
        update_data=update_data,
        current_user=current_user,
    )
