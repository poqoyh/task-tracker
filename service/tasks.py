from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.permissions.projects import can_manage_project
from auth.permissions.tasks import (
    can_manage_task,
    can_view_tasks,
    can_assign_task,
    validate_status_transition,
)
from auth.service import get_user_by_id_service
from crud_repositories.task import (
    get_task_by_id,
    update_task,
    assign_task_to_user,
    unassign_task,
    get_users_tasks,
    get_tasks,
    count_tasks,
    create_task,
)
from db.models import Task, User
from schemas.pagination import PaginatedResponse
from schemas.tasks import TaskUpdate, TaskRead, TaskCreate
from service.projects import get_project_by_id_service, get_project_for_update_service


async def create_task_service(
    session: AsyncSession,
    creating_task: TaskCreate,
    current_user: User,
):
    project = await get_project_for_update_service(
        session=session, project_id=creating_task.project_id
    )

    if not can_manage_project(current_user=current_user, project=project):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to create tasks in this project",
        )

    return await create_task(
        session=session, creating_task=creating_task, project=project
    )


async def get_task_service(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> PaginatedResponse[TaskRead]:
    items = await get_tasks(session=session, limit=limit, offset=offset)
    total = await count_tasks(session=session)

    return PaginatedResponse[TaskRead](
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


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


async def get_users_tasks_service(
    session: AsyncSession,
    user_id: int,
    current_user: User,
):
    target_user = await get_user_by_id_service(session=session, user_id=user_id)

    if not can_view_tasks(current_user=current_user, target_user=target_user):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to view this user's tasks"
        )

    return await get_users_tasks(session=session, user_id=user_id)


async def update_task_service(
    session: AsyncSession,
    task_id: int,
    task_update: TaskUpdate,
    current_user: User,
):

    task = await get_task_by_id_service(
        session=session,
        task_id=task_id,
    )
    if not can_manage_task(current_user=current_user, task=task):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to update this task"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    if "status" in update_data and not validate_status_transition(
        task.status, update_data["status"]
    ):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot transition task from {task.status} to {update_data["status"]}",
        )

    return await update_task(
        session=session,
        task=task,
        task_update=update_data,
    )


async def assign_task_to_user_service(
    session: AsyncSession,
    task_id: int,
    user_id: int,
    current_user: User,
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

    target_user = await get_user_by_id_service(
        session=session,
        user_id=user_id,
    )

    if not can_assign_task(current_user=current_user, target_user=target_user):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to assign this task"
        )

    return await assign_task_to_user(
        session=session,
        task=task,
        user_id=user_id,
    )


async def unassign_task_from_user_service(
    session: AsyncSession,
    task_id: int,
    current_user: User,
):
    task = await get_task_by_id_service(
        session=session,
        task_id=task_id,
    )

    if task.user_id is None:
        raise HTTPException(
            status_code=409,
            detail="Task is not assigned.",
        )

    if not can_manage_task(current_user=current_user, task=task):
        raise HTTPException(
            status_code=403, detail="Not enough permissions to unassign this task"
        )

    return await unassign_task(session=session, task=task)
