from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from crud_repositories.task import create_task, get_tasks

from db import db_helper

from schemas.tasks import TaskRead, TaskCreate
from service.tasks import get_task_by_id_service

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


@router.get("/{task_id}/", response_model=TaskRead)
async def get_task(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    task_id: int,
):
    return await get_task_by_id_service(session=session, task_id=task_id)
