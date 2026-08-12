from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from db.models import User, Team
from schemas.team import TeamUpdate
from service.teams import (
    assign_user_to_team_service,
    get_team_by_id_service,
    update_team_service,
)

"""
GET TEAM BY ID
"""


@pytest.mark.asyncio
async def test_get_team_by_id_success():
    session = AsyncMock()

    team = Team(id=1, name="TestTeam", description="Description for test team")

    with (
        patch(
            "service.teams.get_team_by_id", new=AsyncMock(return_value=team)
        ) as get_team_by_id_mock,
    ):
        result = await get_team_by_id_service(
            session=session,
            team_id=1,
        )

        assert result == team

        get_team_by_id_mock.assert_awaited_once_with(
            session=session,
            team_id=1,
        )


@pytest.mark.asyncio
async def test_get_team_by_id_if_team_not_found():
    session = AsyncMock()

    with (
        patch(
            "service.teams.get_team_by_id",
            new=AsyncMock(return_value=None),
        ) as get_team_by_id_mock,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_team_by_id_service(
                session=session,
                team_id=404,
            )
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Team not found."

        get_team_by_id_mock.assert_awaited_once_with(
            session=session,
            team_id=404,
        )


"""
UPDATE TEAM SERVICE
"""


@pytest.mark.asyncio
async def test_update_team_service_success():
    session = AsyncMock()

    old_team = Team(id=1, name="Old team", description="Old team description")
    updated_team = Team(id=1, name="Updated team", description="Old team description")

    update_shema = TeamUpdate(name="Updated team")

    with (
        patch(
            "service.teams.get_team_by_id_service",
            new=AsyncMock(return_value=old_team),
        ) as get_team_by_id_mock,
        patch(
            "service.teams.update_team",
            new=AsyncMock(return_value=updated_team),
        ) as update_team_mock,
    ):
        result = await update_team_service(
            session=session,
            team_id=1,
            update_data=update_shema,
        )

        assert result == updated_team

        get_team_by_id_mock.assert_awaited_once_with(
            session=session,
            team_id=1,
        )

        update_team_mock.assert_awaited_once_with(
            session=session, team=old_team, update_data={"name": "Updated team"}
        )


@pytest.mark.asyncio
async def test_update_team_service_when_team_not_found():

    session = AsyncMock()

    update_schema = TeamUpdate(name="Updated name")

    with (
        patch(
            "service.teams.get_team_by_id_service",
            side_effect=HTTPException(status_code=404, detail="Team not found."),
        ) as get_team_mock,
        patch("service.teams.update_team", new=AsyncMock()) as update_team_mock,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_team_service(
                session=session,
                team_id=404,
                update_data=update_schema,
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Team not found."

        get_team_mock.assert_awaited_once_with(
            session=session,
            team_id=404,
        )

        update_team_mock.assert_not_awaited()


"""
ASSIGN USER TO TEAM
"""


@pytest.mark.asyncio
async def test_assign_user_to_team_success():

    initial_user = User(
        id=1,
        email="test@test.com",
        username="test",
        team_id=None,
    )

    updated_user = User(
        id=1,
        email="test@test.com",
        username="test",
        team_id=5,
    )

    session = AsyncMock()

    with (
        patch(
            "service.teams.get_user_by_id_service",
            new=AsyncMock(return_value=initial_user),
        ) as get_user_mock,
        patch(
            "service.teams.get_team_by_id_service",
            new=AsyncMock(return_value=True),
        ) as get_team_mock,
        patch(
            "service.teams.assign_user_to_team",
            new=AsyncMock(return_value=updated_user),
        ) as assign_user_to_team_mock,
        patch(
            "service.teams.get_user_by_id_with_team",
            new=AsyncMock(return_value=updated_user),
        ) as get_user_with_team_mock,
    ):
        result = await assign_user_to_team_service(
            session=session,
            user_id=1,
            team_id=5,
        )

        assert result == updated_user
        assert result.team_id == 5

        get_user_mock.assert_awaited_once_with(
            session=session,
            user_id=1,
        )

        get_team_mock.assert_awaited_once_with(
            session=session,
            team_id=5,
        )

        assign_user_to_team_mock.assert_awaited_once_with(
            session=session,
            user=initial_user,
            team_id=5,
        )

        get_user_with_team_mock.assert_awaited_once_with(
            session=session,
            user_id=1,
        )


@pytest.mark.asyncio
async def test_assign_user_to_team_user_already_in_team():

    initial_user_in_team = User(
        id=1,
        email="test@test.com",
        username="test",
        team_id=10,
    )

    session = AsyncMock()

    with (
        patch(
            "service.teams.get_user_by_id_service",
            new=AsyncMock(return_value=initial_user_in_team),
        ) as get_user_mock,
        patch(
            "service.teams.get_team_by_id_service",
            new=AsyncMock(return_value=True),
        ) as get_team_mock,
        patch(
            "service.teams.assign_user_to_team",
            new=AsyncMock(),
        ) as assign_user_to_team_mock,
        patch(
            "service.teams.get_user_by_id_with_team",
            new=AsyncMock(),
        ) as get_user_with_team_mock,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await assign_user_to_team_service(
                session=session,
                user_id=1,
                team_id=5,
            )
        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "User already in a team"

        get_user_mock.assert_awaited_once_with(
            session=session,
            user_id=1,
        )

        get_team_mock.assert_awaited_once_with(
            session=session,
            team_id=5,
        )

        assign_user_to_team_mock.assert_not_awaited()
        get_user_with_team_mock.assert_not_awaited()
