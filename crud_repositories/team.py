from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Team, User


async def create_team(
    session: AsyncSession,
    team_data: dict,
) -> Team:

    team = Team(**team_data)

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


async def get_team_members(
    session: AsyncSession,
    team_id: int,
    limit: int,
    offset: int,
) -> list[User]:
    stmt = (
        select(User)
        .where(User.team_id == team_id)
        .order_by(User.id)
        .limit(limit)
        .offset(offset)
    )

    result = await session.scalars(stmt)

    return result.all()


async def get_teams(
    session: AsyncSession,
    limit: int,
    offset: int,
) -> list[Team]:

    stmt = select(Team).order_by(Team.name).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return result.all()


async def count_teams(session: AsyncSession) -> int:
    result = await session.scalar(select(func.count()).select_from(Team))

    return result or 0


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
) -> User:
    user.team_id = team_id

    await session.commit()
    await session.refresh(user)

    return user


async def remove_user_from_team(
    session: AsyncSession,
    user: User,
) -> User:
    user.team_id = None

    await session.commit()
    await session.refresh(user)

    return user
