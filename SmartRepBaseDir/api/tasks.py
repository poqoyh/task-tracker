from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from crud_repositories.task import create_task

from db import db_helper

from schemas.tasks import TaskRead, TaskCreate

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
