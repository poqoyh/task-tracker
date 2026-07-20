from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from crud_repositories.team import (
    get_team_by_id,
)


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
