from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from db import db_helper

from schemas.team import TeamCreate, TeamRead

from crud_repositories.team import (
    create_team,
    get_all_teams,
)
from schemas.user import UserShortRead

from service.teams import (
    get_team_by_id_service,
    update_team_service,
    assign_user_to_team_service,
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


@router.get("/", response_model=list[TeamRead])
async def get_teams(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    return await get_all_teams(session=session)


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


@router.patch("/{team_id}/", response_model=TeamRead)
async def update_team(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    team_id: int,
    new_team_name: str | None = None,
    new_team_description: str | None = None,
):
    return await update_team_service(
        session=session,
        team_id=team_id,
        new_team_name=new_team_name,
        new_team_description=new_team_description,
    )


@router.post("/{user_id}/{team_id}", response_model=UserShortRead)
async def assign_user_to_team(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    team_id: int,
):
    return await assign_user_to_team_service(
        session=session,
        user_id=user_id,
        team_id=team_id,
    )
