from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Team
from schemas.team import TeamCreate


async def create_team(
    session: AsyncSession,
    creating_team: TeamCreate,
) -> Team:

    team_create = creating_team.model_dump()

    team = Team(**team_create)

    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team
