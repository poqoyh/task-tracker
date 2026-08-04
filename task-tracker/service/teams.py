from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from auth.service import get_user_by_id_service
from crud_repositories.team import (
    get_team_by_id,
    update_team,
    assign_user_to_team,
    remove_user_from_team,
    get_team_members,
)
from crud_repositories.user import get_user_by_id_with_team

from schemas.team import TeamUpdate


async def get_team_by_id_service(
    session: AsyncSession,
    team_id: int,
):
    team = await get_team_by_id(session, team_id)

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found.",
        )

    return team


async def get_team_members_service(
    session: AsyncSession,
    team_id: int,
):
    await get_team_by_id_service(session=session, team_id=team_id)

    return await get_team_members(session=session, team_id=team_id)


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
