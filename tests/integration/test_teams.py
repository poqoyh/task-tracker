import pytest

from db.models import User

pytestmark = pytest.mark.asyncio


"""
Create team
"""


async def test_admin_create_team_success(admin_client):
    response = await admin_client.post(
        "/api/team/", json={"name": "Backend", "description": "Backend team"}
    )

    assert response.status_code == 200

    body = response.json()
    assert body["name"] == "Backend"
    assert body["description"] == "Backend team"

    team_id = body["id"]
    get_response = await admin_client.get(f"/api/team/{team_id}/")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Backend"


async def test_admin_create_team_missing_description_returns_422(admin_client):

    response = await admin_client.post("/api/team/", json={"name": "Backend"})

    assert response.status_code == 422


async def test_admin_create_team_duplicate_name_fails(admin_client, create_team):

    await create_team()

    response = await admin_client.post(
        "/api/team/",
        json={"name": "Backend", "description": "Second team"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Team with this name already exists."


async def test_team_lead_create_team_forbidden(team_lead_client):
    response = await team_lead_client.post(
        "/api/team/", json={"name": "Backend", "description": "Backend team"}
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions"


"""
Get teams
"""


async def test_admin_get_teams_success(admin_client, create_team):

    await create_team()
    await create_team(
        name="Frontend",
        description="Frontend team",
    )

    response = await admin_client.get("/api/team/")

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 2

    assert {team["name"] for team in body["items"]} == {"Backend", "Frontend"}

    assert body["total"] == 2


async def test_admin_get_teams_empty_list(admin_client):

    response = await admin_client.get("/api/team/")

    body = response.json()

    assert body["items"] == []

    assert body["total"] == 0


async def test_team_lead_get_teams_forbidden(team_lead_client, create_team):
    await create_team()

    response = await team_lead_client.get("/api/team/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions"


"""
Get my team
"""


async def test_get_my_team_success(
    worker_client,
    worker_user,
    session,
    create_team,
):

    team = await create_team()

    worker_user.team_id = team["id"]
    await session.commit()

    response = await worker_client.get("/api/team/me/team/")

    assert response.status_code == 200
    assert response.json()["name"] == "Backend"


async def test_get_my_team_if_team_is_none(worker_client):

    response = await worker_client.get("/api/team/me/team/")

    assert response.status_code == 404
    assert response.json()["detail"] == "User is not in a team"


"""
Get team by id
"""


async def test_admin_get_team_by_id_success(admin_client, create_team):

    team = await create_team(name="Backend", description="Backend developer team")

    response = await admin_client.get(f"/api/team/{team['id']}/")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == team["id"]
    assert body["name"] == "Backend"
    assert body["description"] == "Backend developer team"


async def test_admin_get_team_by_id_not_found(admin_client):

    response = await admin_client.get("/api/team/999/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Team not found."


async def test_team_lead_get_team_success(
    session, team_lead_client, team_lead_user, create_team
):

    team = await create_team()

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    response = await team_lead_client.get(f"/api/team/{team['id']}/")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == team["id"]
    assert body["name"] == "Backend"
    assert body["description"] == "Backend team"


async def test_team_lead_get_team_forbidden(session, team_lead_client, create_team):

    team = await create_team()

    response = await team_lead_client.get(f"/api/team/{team['id']}/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this team"


async def test_worker_get_team_forbidden(session, worker_client, create_team):

    team = await create_team()

    response = await worker_client.get(f"/api/team/{team['id']}/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this team"


"""
Get team members
"""


async def test_admin_get_team_members_success(admin_client, session, create_team):
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

    response = await admin_client.get(f"/api/team/{team['id']}/members")

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 2
    assert {user["username"] for user in body["items"]} == {
        "user1",
        "user2",
    }
    assert body["total"] == 2


async def test_admin_get_team_members_team_empty(admin_client, create_team):

    team = await create_team()

    response = await admin_client.get(f"/api/team/{team['id']}/members")

    assert response.status_code == 200

    body = response.json()

    assert body["items"] == []
    assert body["total"] == 0


async def test_team_lead_get_team_members_success(
    session, team_lead_client, team_lead_user, worker_user, create_team
):
    team = await create_team()

    worker_user.team_id = team["id"]
    team_lead_user.team_id = team["id"]

    session.add_all([worker_user, team_lead_user])
    await session.commit()

    response = await team_lead_client.get(f"/api/team/{team['id']}/members")

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 2
    assert {user["username"] for user in body["items"]} == {
        "lead",
        "worker",
    }
    assert body["total"] == 2


async def test_team_lead_get_team_members_forbidden(
    session, team_lead_client, create_team
):
    team = await create_team()

    response = await team_lead_client.get(f"/api/team/{team['id']}/members")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this team"


async def test_worker_get_team_members_forbidden(session, worker_client, create_team):
    team = await create_team()

    response = await worker_client.get(f"/api/team/{team['id']}/members")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this team"


"""
Update team
"""


async def test_admin_update_team_success_with_two_params(admin_client, create_team):
    team = await create_team()

    response = await admin_client.patch(
        f"/api/team/{team['id']}/",
        json={"name": "new_name", "description": "new_description"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "new_name"
    assert body["description"] == "new_description"


async def test_admin_update_team_success_with_name(admin_client, create_team):
    team = await create_team()

    response = await admin_client.patch(
        f"/api/team/{team['id']}/",
        json={"name": "new_name"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "new_name"
    assert body["description"] == "Backend team"


async def test_admin_update_team_success_with_description(admin_client, create_team):
    team = await create_team()

    response = await admin_client.patch(
        f"/api/team/{team['id']}/",
        json={"description": "new_description"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Backend"
    assert body["description"] == "new_description"


async def test_admin_update_team_success_with_empty(admin_client, create_team):
    team = await create_team()

    response = await admin_client.patch(f"/api/team/{team['id']}/", json={})

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Backend"
    assert body["description"] == "Backend team"


async def test_team_lead_update_team_success(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    response = await team_lead_client.patch(
        f"/api/team/{team['id']}/",
        json={"name": "new_name", "description": "new_description"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "new_name"
    assert body["description"] == "new_description"


async def test_team_lead_update_team_forbidden(
    team_lead_client,
    create_team,
):
    team = await create_team()

    response = await team_lead_client.patch(
        f"/api/team/{team['id']}/",
        json={"name": "new_name", "description": "new_description"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this team"


async def test_worker_update_team_forbidden(
    worker_client,
    create_team,
):
    team = await create_team()

    response = await worker_client.patch(
        f"/api/team/{team['id']}/",
        json={"name": "new_name", "description": "new_description"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this team"


async def test_admin_update_team_integrity_error(
    admin_client,
    create_team,
):
    team_1 = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend Team")

    response = await admin_client.patch(
        f"/api/team/{team_1['id']}/",
        json={"name": "Frontend"},
    )

    assert response.status_code == 409

    body = response.json()

    assert body["detail"] == "Name already taken"


"""
Assign user to team
"""


async def test_admin_assign_user_to_team(admin_client, session, create_team):
    team = await create_team()

    user_1 = User(
        username="user1",
        email="user1@mail.com",
        hashed_password="fake123",
        team_id=None,
    )

    session.add(user_1)
    await session.commit()
    await session.refresh(user_1)

    response = await admin_client.patch(f"/api/team/{user_1.id}/{team['id']}")

    assert response.status_code == 200

    body = response.json()

    assert body["team"]["id"] == team["id"]


async def test_admin_assign_user_to_team_if_team_id_is_not_none(
    admin_client, session, create_team
):

    backend_team = await create_team()

    frontend_team = await create_team(name="Frontend", description="Frontend team")

    user_1 = User(
        username="user1",
        email="user1@mail.com",
        hashed_password="fake123",
        team_id=backend_team["id"],
    )

    session.add(user_1)
    await session.commit()
    await session.refresh(user_1)

    response = await admin_client.patch(f"/api/team/{user_1.id}/{frontend_team['id']}")

    assert response.status_code == 409
    assert response.json()["detail"] == "User already in a team"


async def test_team_lead_assign_user_to_team_success(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    create_team,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    response = await team_lead_client.patch(f"/api/team/{worker_user.id}/{team['id']}")

    assert response.status_code == 200

    body = response.json()

    assert body["team"]["id"] == team["id"]


async def test_team_lead_assign_user_to_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    create_team,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend Team")

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    response = await team_lead_client.patch(
        f"/api/team/{worker_user.id}/{team_2['id']}"
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this team"


async def test_team_lead_assign_user_to_team_forbidden(
    team_lead_client,
    worker_user,
    create_team,
):
    team = await create_team()

    response = await team_lead_client.patch(f"/api/team/{worker_user.id}/{team['id']}")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this team"


async def test_worker_assign_user_to_team_forbidden(
    worker_client,
    worker_user,
    create_team,
):
    team = await create_team()

    response = await worker_client.patch(f"/api/team/{worker_user.id}/{team['id']}")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this team"


"""
Remove user from team
"""


async def test_admin_remove_user_from_team_success(admin_client, session, create_team):
    team = await create_team()

    user_1 = User(
        username="user1",
        email="user1@mail.com",
        hashed_password="fake123",
        team_id=team["id"],
    )

    session.add(user_1)
    await session.commit()
    await session.refresh(user_1)

    response = await admin_client.patch(f"/api/team/remove-user/{user_1.id}")

    assert response.status_code == 200

    body = response.json()

    assert body["team"] is None


async def test_admin_remove_user_from_team_if_team_none(admin_client, session):

    user_1 = User(
        username="user1",
        email="user1@mail.com",
        hashed_password="fake123",
        team_id=None,
    )

    session.add(user_1)
    await session.commit()
    await session.refresh(user_1)

    response = await admin_client.patch(f"/api/team/remove-user/{user_1.id}")

    assert response.status_code == 409
    assert response.json()["detail"] == "User is not in a team"


async def test_team_lead_remove_user_from_team_success(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    create_team,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.patch(f"/api/team/remove-user/{worker_user.id}")

    assert response.status_code == 200

    body = response.json()

    assert body["team"] is None


async def test_team_lead_remove_user_from_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    create_team,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend Team")

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.patch(f"/api/team/remove-user/{worker_user.id}")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to remove user from this team"


async def test_team_lead_without_remove_user_from_team_forbidden(
    session,
    team_lead_client,
    worker_user,
    create_team,
):
    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    response = await team_lead_client.patch(f"/api/team/remove-user/{worker_user.id}")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to remove user from this team"


async def test_worker_remove_user_from_team_forbidden(
    session,
    worker_client,
    worker_user,
    create_team,
):
    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    response = await worker_client.patch(f"/api/team/remove-user/{worker_user.id}")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to remove user from this team"
