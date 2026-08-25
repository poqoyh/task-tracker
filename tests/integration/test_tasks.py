import pytest

pytest = pytest.mark.asyncio


"""
Get Users Tasks 
"""


async def test_worker_get_himself_tasks_success(
    worker_client,
    worker_user,
    admin_client,
    create_task,
):
    task = await create_task()

    await admin_client.post(f"/api/task/{task["id"]}/assign/{worker_user.id}")

    response = await worker_client.get(f"/api/task/users/{worker_user.id}/tasks")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == task["id"]
    assert body[0]["name"] == "Test task"


async def test_worker_get_task_worker(
    worker_client,
    worker_user,
    second_worker_user,
    admin_client,
    create_task,
):
    task = await create_task()

    await admin_client.post(f"/api/task/{task["id"]}/assign/{worker_user.id}")

    response = await worker_client.get(f"/api/task/users/{second_worker_user.id}/tasks")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this user's tasks"


async def test_team_lead_get_task_worker_in_his_team(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    admin_client,
    create_task,
    create_team,
):
    task = await create_task()
    team = await create_team()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    response = await team_lead_client.get(f"/api/task/users/{worker_user.id}/tasks")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == task["id"]
    assert body[0]["name"] == "Test task"


async def test_team_lead_get_task_worker_in_another_team(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    admin_client,
    create_team,
):

    team = await create_team()
    team_2 = await create_team(
        name="Frontend",
        description="Frontend Team",
    )

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.get(f"/api/task/users/{worker_user.id}/tasks")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this user's tasks"


async def test_team_lead_get_task_without_team(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    admin_client,
    create_team,
):

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    response = await team_lead_client.get(f"/api/task/users/{worker_user.id}/tasks")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this user's tasks"


async def test_admin_get_task_success(
    session,
    worker_user,
    admin_client,
    create_task,
    create_team,
):
    task = await create_task()
    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    response = await admin_client.get(f"/api/task/users/{worker_user.id}/tasks")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["id"] == task["id"]
    assert body[0]["name"] == "Test task"
