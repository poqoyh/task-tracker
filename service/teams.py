from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession

from auth.service import get_user_by_id_service
from crud_repositories.team import (
    get_team_by_id,
    update_team,
    assign_user_to_team,
    remove_user_from_team,
    get_team_members,
    create_team,
    get_teams,
    count_teams,
    count_team_members,
)
from crud_repositories.user import get_user_by_id_with_team
from schemas.pagination import PaginatedResponse

from schemas.team import TeamUpdate, TeamCreate, TeamRead
from schemas.user import UserShortRead


async def get_teams_service(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> PaginatedResponse[TeamRead]:
    items = await get_teams(session=session, limit=limit, offset=offset)
    total = await count_teams(session=session)

    return PaginatedResponse[TeamRead](
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_team_by_id_service(
    session: AsyncSession,
    team_id: int,
):
    team = await get_team_by_id(session=session, team_id=team_id)

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found.",
        )

    return team


async def create_team_service(
    session: AsyncSession,
    creating_team: TeamCreate,
):
    team_data = creating_team.model_dump()

    try:
        return await create_team(
            session=session,
            team_data=team_data,
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Team with this name already exists.",
        )


async def get_team_members_service(
    session: AsyncSession,
    team_id: int,
    limit: int,
    offset: int,
) -> PaginatedResponse[UserShortRead]:
    await get_team_by_id_service(session=session, team_id=team_id)

    items = await get_team_members(
        session=session, team_id=team_id, limit=limit, offset=offset
    )
    total = await count_team_members(session, team_id=team_id)

    return PaginatedResponse[UserShortRead](
        items=items, total=total, limit=limit, offset=offset
    )


async def update_team_service(
    session: AsyncSession,
    team_id: int,
    update_data: TeamUpdate,
):
    team = await get_team_by_id_service(
        session=session,
        team_id=team_id,
    )

    update_data = update_data.model_dump(exclude_unset=True)

    return await update_team(
        session=session,
        team=team,
        update_data=update_data,
    )


async def get_current_user_team_service(
    session: AsyncSession,
    user_id: int,
):
    user = await get_user_by_id_service(
        session=session,
        user_id=user_id,
    )

    if user.team_id is None:
        raise HTTPException(
            status_code=404,
            detail="User is not in a team",
        )

    return await get_team_by_id_service(session=session, team_id=user.team_id)


async def assign_user_to_team_service(
    session: AsyncSession,
    user_id: int,
    team_id: int,
):
    user = await get_user_by_id_service(
        session=session,
        user_id=user_id,
    )

    await get_team_by_id_service(
        session=session,
        team_id=team_id,
    )

    if user.team_id is not None:
        raise HTTPException(
            status_code=409,
            detail="User already in a team",
        )

    await assign_user_to_team(
        session=session,
        user=user,
        team_id=team_id,
    )

    return await get_user_by_id_with_team(session=session, user_id=user_id)


async def remove_user_from_team_service(
    session: AsyncSession,
    user_id: int,
):
    user = await get_user_by_id_service(
        session=session,
        user_id=user_id,
    )

    if user.team_id is None:
        raise HTTPException(
            status_code=409,
            detail="User is not in a team",
        )

    return await remove_user_from_team(
        session=session,
        user=user,
    )
