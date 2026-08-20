from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
)

from auth.dependencies import get_current_user, require_role
from db import db_helper
from db.models import User
from db.models.user import UserRole
from schemas.pagination import PaginationParams

from schemas.team import TeamCreate, TeamRead, TeamUpdate

from crud_repositories.team import (
    get_all_teams,
)
from schemas.user import UserShortRead, UserReadWithTeam

from service.teams import (
    get_team_by_id_service,
    update_team_service,
    assign_user_to_team_service,
    remove_user_from_team_service,
    get_team_members_service,
    get_current_user_team_service,
    create_team_service,
)

router = APIRouter(tags=["Teams"])


@router.post("/", response_model=TeamRead)
async def create(
    team: TeamCreate,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await create_team_service(
        session=session,
        creating_team=team,
    )


@router.get("/", response_model=list[TeamRead])
async def get_teams(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    pagination: Annotated[PaginationParams, Depends()],
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_all_teams(
        session=session, limit=pagination.limit, offset=pagination.offset
    )


@router.get("/me/team/", response_model=TeamRead)
async def get_my_team(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    _: User = Depends(
        require_role(UserRole.ADMIN, UserRole.TEAM_LEAD, UserRole.WORKER)
    ),
):
    return await get_current_user_team_service(
        session=session, user_id=int(current_user.id)
    )


@router.get("/{team_id}/", response_model=TeamRead)
async def get_team(
    team_id: int,
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_team_by_id_service(
        session=session,
        team_id=team_id,
    )


@router.get("/{team_id}/members", response_model=list[UserShortRead])
async def get_team_members(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    team_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await get_team_members_service(session=session, team_id=team_id)


@router.patch("/{team_id}/", response_model=TeamRead)
async def update_team(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    team_id: int,
    update_data: TeamUpdate,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await update_team_service(
        session=session,
        team_id=team_id,
        update_data=update_data,
    )


@router.patch("/remove-user/{user_id}", response_model=UserReadWithTeam)
async def remove_user_from_team(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await remove_user_from_team_service(
        session=session,
        user_id=user_id,
    )


@router.patch("/{user_id}/{team_id}", response_model=UserReadWithTeam)
async def assign_user_to_team(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_id: int,
    team_id: int,
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.TEAM_LEAD)),
):
    return await assign_user_to_team_service(
        session=session,
        user_id=user_id,
        team_id=team_id,
    )
