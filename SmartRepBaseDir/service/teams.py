from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from auth.service import get_user_by_id_service
from crud_repositories.team import (
    get_team_by_id,
    update_team,
)
from crud_repositories.user import get_user_by_id_with_team


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


async def update_team_service(
    session: AsyncSession,
    team_id: int,
    new_team_name: str | None,
    new_team_description: str | None,
):
    team = await get_team_by_id_service(
        session=session,
        team_id=team_id,
    )

    return await update_team(
        session=session,
        team=team,
        new_team_name=new_team_name,
        new_team_description=new_team_description,
    )


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

    user.team_id = team_id
    await session.commit()

    return await get_user_by_id_with_team(session=session, user_id=user_id)
