from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from crud_repositories.task import create_task, get_tasks

from db import db_helper

from schemas.tasks import TaskRead, TaskCreate, TaskUpdate
from service.tasks import (
    get_task_by_id_service,
    update_task_service,
    assign_task_to_user_service,
)

router = APIRouter(tags=["Tasks"])


@router.post("/", response_model=TaskRead)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task: TaskCreate,
):
    return await create_task(session=session, creating_task=task)


@router.get("/", response_model=list[TaskRead])
async def get_all_tasks(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await get_tasks(session=session)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
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
):
    return await update_task_service(
        session=session,
        task_id=task_id,
        task_update=task_update,
    )


@router.post("/{task_id}/assign/{user_id}")
async def assign_task_to_user(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
    user_id: int,
):

    return await assign_task_to_user_service(
        session=session,
        task_id=task_id,
        user_id=user_id,
    )
