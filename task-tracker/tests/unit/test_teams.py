from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from db.models import User
from service.teams import assign_user_to_team_service

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
