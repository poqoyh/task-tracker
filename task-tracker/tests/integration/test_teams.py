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


async def test_create_team_duplicate_name_fails(client):

    await client.post(
        "api/team/",
        json={"name": "Backend", "description": "First team"},
    )

    response = await client.post(
        "api/team/",
        json={"name": "Backend", "description": "Second team"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Team with this name already exists."


"""
Get team by id
"""


async def test_get_team_by_id_success(client):

    create_response = await client.post(
        "/api/team/",
        json={"name": "Backend", "description": "Backend development team"},
    )

    assert create_response.status_code == 200

    team_id = create_response.json()["id"]

    response = await client.get(f"/api/team/{team_id}/")

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == team_id
    assert body["name"] == "Backend"
    assert body["description"] == "Backend development team"


async def test_get_team_by_id_not_found(client):

    response = await client.get("/api/team/999/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found."


"""
Get my team
"""


async def test_get_my_team_success(client, session):

    team = Team(name="Backend", description="Backend team")
    session.add(team)
    await session.commit()
    await session.refresh(team)

    user = User(
        email="test@test.com",
        username="testuser",
        hashed_password="fakehash",
        team_id=team.id,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    async def override_get_current_user():
        return user

    from main import main_app

    main_app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.get("/api/team/me/team/")

    assert response.status_code == 200
    assert response.json()["name"] == "Backend"

    main_app.dependency_overrides.pop(get_current_user, None)
