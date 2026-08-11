from unittest.mock import AsyncMock, patch

import pytest

from db.models import User
from service.teams import assign_user_to_team_service


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
