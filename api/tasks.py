from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from auth.dependencies import require_role, get_current_user
from crud_repositories.task import create_task

from db import db_helper
from db.models import User
from db.models.user import UserRole

from schemas.pagination import PaginationParams, PaginatedResponse

from schemas.tasks import TaskRead, TaskCreate, TaskUpdate
from service.tasks import (
    get_task_by_id_service,
    update_task_service,
    assign_task_to_user_service,
    unassign_task_from_user_service,
    get_users_tasks_service,
    get_task_service,
)

router = APIRouter(tags=["Tasks"])


@router.post("/", response_model=TaskRead)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task: TaskCreate,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await create_task(session=session, creating_task=task)


@router.get("/", response_model=PaginatedResponse[TaskRead])
async def get_all_tasks(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    pagination: Annotated[PaginationParams, Depends()],
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_task_service(
        session=session,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/users/{user_id}/tasks", response_model=list[TaskRead])
async def get_user_tasks(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_users_tasks_service(session=session, user_id=user_id)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
):
    return await get_task_by_id_service(session=session, task_id=task_id)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
):
    return await update_task_service(
        session=session,
        task_id=task_id,
        task_update=task_update,
        current_user=current_user,
    )


@router.post("/{task_id}/assign/{user_id}")
async def assign_task_to_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
    user_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):

    return await assign_task_to_user_service(
        session=session,
        task_id=task_id,
        user_id=user_id,
    )


@router.patch("/{task_id}/unassign")
async def unassign_task(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    return await unassign_task_from_user_service(
        session=session,
        task_id=task_id,
        current_user=current_user,
    )
