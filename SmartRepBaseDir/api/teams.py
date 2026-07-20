from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from db import db_helper

from schemas.team import TeamCreate, TeamRead

from crud_repositories.team import create_team

from service.teams import (
    get_team_by_id_service,
)

router = APIRouter(tags=["Teams"])


@router.post("/", response_model=TeamRead)
async def create(
    team: TeamCreate,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await create_team(
        session=session,
        creating_team=team,
    )


@router.get("/{team_id}/", response_model=TeamRead)
async def get_team(
    team_id: int,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await get_team_by_id_service(
        session=session,
        team_id=team_id,
    )
