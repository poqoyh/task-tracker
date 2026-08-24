import pytest

pytestmark = pytest.mark.asyncio


"""
Update user
"""


async def test_update_user_worker_self_success(worker_client, worker_user):

    response = await worker_client.patch(
        f"api/users/{worker_user.id}", json={"username": "NewName"}
    )

    assert response.status_code == 200

    body = response.json()

    assert body["username"] == "NewName"


async def test_update_user_worker_another_worker(
    worker_client,
    worker_user,
    second_worker_user,
):

    response = await worker_client.patch(
        f"api/users/{second_worker_user.id}", json={"username": "NewName"}
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this user"


async def test_update_user_team_lead_team_worker(
    session,
    team_lead_client,
    worker_user,
    team_lead_user,
    create_team,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.patch(
        f"api/users/{worker_user.id}", json={"username": "NewName"}
    )

    assert response.status_code == 200

    body = response.json()

    assert body["username"] == "NewName"


async def test_update_user_team_lead_another_team_worker(
    session,
    team_lead_client,
    worker_user,
    team_lead_user,
    create_team,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend Team")

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.patch(
        f"api/users/{worker_user.id}", json={"username": "NewName"}
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this user"


async def test_update_user_team_lead_without_team_another_team_worker(
    session,
    team_lead_client,
    worker_user,
    team_lead_user,
    create_team,
):
    team_2 = await create_team(name="Frontend", description="Frontend Team")

    worker_user.team_id = team_2["id"]

    session.add(worker_user)
    await session.commit()

    response = await team_lead_client.patch(
        f"api/users/{worker_user.id}", json={"username": "NewName"}
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this user"


async def test_update_user_team_lead_without_team_himself(
    team_lead_client, team_lead_user
):

    response = await team_lead_client.patch(
        f"api/users/{team_lead_user.id}", json={"username": "NewName"}
    )

    assert response.status_code == 200

    body = response.json()

    assert body["username"] == "NewName"


async def test_update_user_admin(
    admin_client,
    team_lead_user,
):

    response = await admin_client.patch(
        f"api/users/{team_lead_user.id}", json={"username": "NewName"}
    )

    assert response.status_code == 200

    body = response.json()

    assert body["username"] == "NewName"
