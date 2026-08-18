import pytest

from auth.dependencies import get_current_user
from db.models import Team, User

pytestmark = pytest.mark.asyncio


"""
Create team
"""


async def test_create_team_success(client):
    response = await client.post(
        "/api/team/", json={"name": "Backend", "description": "Backend team"}
    )

    assert response.status_code == 200

    body = response.json()
    assert body["name"] == "Backend"
    assert body["description"] == "Backend team"

    team_id = body["id"]
    get_response = await client.get(f"/api/team/{team_id}/")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Backend"


async def test_create_team_missing_description_returns_422(client):

    response = await client.post("/api/team/", json={"name": "Backend"})

    assert response.status_code == 422


async def test_create_team_duplicate_name_fails(client, create_team):

    await create_team()

    response = await client.post(
        "api/team/",
        json={"name": "Backend", "description": "Second team"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Team with this name already exists."


"""
Get teams
"""


async def test_get_teams_success(client, create_team):

    await create_team()
    await create_team(
        name="Frontend",
        description="Frontend team",
    )

    response = await client.get("/api/team/")

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 2

    assert {team["name"] for team in body} == {"Backend", "Frontend"}


async def test_get_teams_empty_list(client):

    response = await client.get("/api/team/")

    assert response.status_code == 200
    assert response.json() == []


"""
Get my team
"""


async def test_get_my_team_success(client, session, create_team, authenticated_user):

    team = await create_team()
    authenticated_user.team_id = team["id"]

    session.add(authenticated_user)
    await session.commit()

    response = await client.get("/api/team/me/team/")

    assert response.status_code == 200
    assert response.json()["name"] == "Backend"


async def test_get_my_team_if_team_is_none(client, authenticated_user):

    response = await client.get("/api/team/me/team/")

    assert response.status_code == 404
    assert response.json()["detail"] == "User is not in a team"


"""
Get team by id
"""


async def test_get_team_by_id_success(client, create_team):

    team = await create_team(name="Backend", description="Backend developer team")

    response = await client.get(f"/api/team/{team["id"]}/")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == team["id"]
    assert body["name"] == "Backend"
    assert body["description"] == "Backend developer team"


async def test_get_team_by_id_not_found(client):

    response = await client.get("/api/team/999/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found."


"""
Get team members
"""


async def test_get_team_members_success(client, session, create_team):
    team = await create_team()

    user_1 = User(
        username="user1",
        email="user1@mail.com",
        hashed_password="fake123",
        team_id=team["id"],
    )

    user_2 = User(
        username="user2",
        email="user2@mail.com",
        hashed_password="fake123",
        team_id=team["id"],
    )

    session.add_all([user_1, user_2])
    await session.commit()

    response = await client.get(f"/api/team/{team['id']}/members")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert {user["username"] for user in body} == {"user1", "user2"}


async def test_get_team_members_team_empty(client, create_team):

    team = await create_team()

    response = await client.get(f"/api/team/{team['id']}/members")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 0
