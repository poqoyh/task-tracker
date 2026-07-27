from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Team, User
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


async def get_team_by_id(
    session: AsyncSession,
    team_id: int,
) -> Team | None:

    stmt = select(Team).where(Team.id == team_id)

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def get_all_teams(
    session: AsyncSession,
) -> list[Team] | list[None]:

    stmt = select(Team).order_by(Team.name)

    result = await session.scalars(stmt)

    return result.all()


async def update_team(
    session: AsyncSession,
    team: Team,
    update_data: dict,
) -> Team:

    for field, value in update_data.items():
        setattr(team, field, value)

    await session.commit()
    await session.refresh(team)

    return team


async def assign_user_to_team(
    session: AsyncSession,
    user: User,
    team_id: int,
):
    user.team_id = team_id

    await session.commit()
    await session.refresh(user)

    return user
