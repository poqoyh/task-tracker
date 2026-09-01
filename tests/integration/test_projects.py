import pytest

pytest = pytest.mark.asyncio


"""
Create project
"""


async def test_admin_create_project_success(
    admin_client,
    create_team,
):
    team = await create_team()

    response = await admin_client.post(
        "/api/project/",
        json={
            "name": "Backend for bank",
            "key": "BKD",
            "description": "Test Project",
            "team_id": team["id"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["name"] == "Backend for bank"
    assert body["key"] == "BKD"
    assert body["team_id"] == team["id"]


async def test_admin_create_project_409(
    admin_client,
    create_team,
    create_project,
):
    team = await create_team()
    team_2 = await create_team("Back")

    await create_project(team_id=team_2["id"])

    response = await admin_client.post(
        "/api/project/",
        json={
            "name": "Backend for bank",
            "key": "BKD",
            "description": "Test Project",
            "team_id": team["id"],
        },
    )

    assert response.status_code == 409

    body = response.json()

    assert body["detail"] == "Project with this key already exist."


async def test_team_lead_create_project_with_own_team_success(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
):

    team = await create_team()

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    response = await team_lead_client.post(
        "/api/project/",
        json={
            "name": "Backend for bank",
            "key": "BKD",
            "description": "Test Project",
            "team_id": team["id"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["name"] == "Backend for bank"
    assert body["key"] == "BKD"
    assert body["team_id"] == team["id"]


async def test_team_lead_create_project_with_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
):

    team = await create_team()
    team_2 = await create_team("Frontend")

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    response = await team_lead_client.post(
        "/api/project/",
        json={
            "name": "Backend for bank",
            "key": "BKD",
            "description": "Test Project",
            "team_id": team_2["id"],
        },
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to create a project for this team"


async def test_team_lead_without_team_create_project_forbidden(
    team_lead_client,
    create_team,
):
    team = await create_team()

    response = await team_lead_client.post(
        "/api/project/",
        json={
            "name": "Backend for bank",
            "key": "BKD",
            "description": "Test Project",
            "team_id": team["id"],
        },
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to create a project for this team"


async def test_worker_create_project_forbidden(
    worker_client,
    create_team,
):
    team = await create_team()

    response = await worker_client.post(
        "/api/project/",
        json={
            "name": "Backend for bank",
            "key": "BKD",
            "description": "Test Project",
            "team_id": team["id"],
        },
    )

    assert response.status_code == 403


"""
Get all projects
"""


async def test_admin_get_all_projects_success(
    admin_client,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    response = await admin_client.get("/api/project/")

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 1

    assert body["total"] == 1


async def test_team_lead_get_all_projects_success(
    team_lead_client,
):

    response = await team_lead_client.get("/api/project/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions"


async def test_worker_get_all_projects_forbidden(
    worker_client,
):
    response = await worker_client.get("/api/project/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions"


"""
Get project
"""


async def test_admin_get_project_success(
    admin_client,
    create_team,
    create_project,
):

    team = await create_team()
    project = await create_project(team_id=team["id"])

    response = await admin_client.get(f"/api/project/{project["id"]}/")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["name"] == "Backend Project"


async def test_team_lead_get_project_success(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
    create_project,
):

    team = await create_team()

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team["id"])

    response = await team_lead_client.get(f"/api/project/{project["id"]}/")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["name"] == "Backend Project"


async def test_team_lead_without_team_get_project_forbidden(
    team_lead_client,
    create_team,
    create_project,
):

    team = await create_team()

    project = await create_project(team_id=team["id"])

    response = await team_lead_client.get(f"/api/project/{project["id"]}/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permission to view this project"


async def test_team_lead_get_project_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
    create_project,
):

    team = await create_team()
    team_2 = await create_team("Frontend")

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team_2["id"])

    response = await team_lead_client.get(f"/api/project/{project["id"]}/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permission to view this project"


async def test_worker_get_project_forbidden(
    session,
    worker_client,
    create_team,
    create_project,
):

    team = await create_team()

    project = await create_project(team_id=team["id"])

    response = await worker_client.get(f"/api/project/{project["id"]}/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permission to view this project"


async def test_admin_update_project_success(
    admin_client,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    response = await admin_client.patch(
        f"/api/project/{project["id"]}/",
        json={
            "name": "New Name",
            "description": "Description",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "New Name"
    assert body["description"] == "Description"


async def test_team_lead_update_project_own_team_success(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
    create_project,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team["id"])

    response = await team_lead_client.patch(
        f"/api/project/{project['id']}/",
        json={"name": "New Name"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "New Name"


async def test_team_lead_update_project_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
    create_project,
):
    team = await create_team()
    team_2 = await create_team("Frontend")

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team_2["id"])

    response = await team_lead_client.patch(
        f"/api/project/{project['id']}/",
        json={"name": "New Name"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this project"


async def test_team_lead_without_team_update_project_forbidden(
    team_lead_client,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    response = await team_lead_client.patch(
        f"/api/project/{project['id']}/",
        json={"name": "New Name"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this project"


async def test_worker_update_project_forbidden(
    worker_client,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    response = await worker_client.patch(
        f"/api/project/{project['id']}/",
        json={"name": "New Name"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this project"
