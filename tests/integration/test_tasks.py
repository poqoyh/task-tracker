import pytest

from db.models import Task

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


"""
Update task
"""


async def test_admin_update_task_success(
    session,
    admin_client,
    create_task,
):
    task = await create_task()

    response = await admin_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == task["id"]
    assert body["name"] == "Updated Task Name"
    assert body["description"] == "Updated Task Description"


async def test_team_lead_update_task_success(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    create_team,
    create_task,
):
    team = await create_team()
    task = await create_task()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    await team_lead_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    response = await team_lead_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == task["id"]
    assert body["name"] == "Updated Task Name"
    assert body["description"] == "Updated Task Description"


async def test_team_lead_update_task_in_another_team(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    admin_client,
    create_team,
    create_task,
):
    team = await create_team()
    team_2 = await create_team(
        name="Frontend",
        description="Frontend team",
    )

    task = await create_task()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    response = await team_lead_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this task"


async def test_team_lead_update_unappointed_task(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    create_team,
    create_task,
):
    team = await create_team()
    task = await create_task()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this task"


async def test_team_lead_without_team_update_task(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    admin_client,
    create_team,
    create_task,
):
    team = await create_team()
    task = await create_task()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    response = await team_lead_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this task"


async def test_worker_update_his_task(
    session,
    worker_client,
    worker_user,
    admin_client,
    create_team,
    create_task,
):
    team = await create_team()
    task = await create_task()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    response = await worker_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this task"


"""
Assign task to user
"""


async def test_test_admin_assign_task_to_user(
    worker_user,
    admin_client,
    create_task,
):
    task = await create_task()

    response = await admin_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["user_id"] == 1


async def test_team_lead_assign_task_to_worker(
    session,
    worker_user,
    team_lead_client,
    team_lead_user,
    create_task,
    create_team,
):
    task = await create_task()
    team = await create_team()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["user_id"] == 1


async def test_team_lead_assign_task_to_worker_in_another_team(
    session,
    worker_user,
    team_lead_client,
    team_lead_user,
    create_task,
    create_team,
):
    task = await create_task()

    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend Team")

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to assign this task"


async def test_team_lead_without_team_assign_task_to_worker(
    session,
    worker_user,
    team_lead_client,
    create_task,
    create_team,
):
    task = await create_task()

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    response = await team_lead_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to assign this task"


async def test_worker_assign_task(
    session,
    worker_client,
    worker_user,
    create_task,
    create_team,
):
    task = await create_task()

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    response = await worker_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to assign this task"


async def test_admin_assign_task_that_has_already_been_assigned(
    session,
    admin_client,
    worker_user,
    create_task,
    create_team,
):
    task = await create_task()

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    first_response = await admin_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert first_response.status_code == 200

    response = await admin_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert response.status_code == 409

    body = response.json()

    assert body["detail"] == "Task already assigned."


"""
Unassign task
"""


async def test_admin_unassign_task_to_worker(
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

    assign_response = await admin_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert assign_response.status_code == 200

    response = await admin_client.patch(f"/api/task/{task['id']}/unassign")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["user_id"] is None


async def test_team_lead_unassign_task_to_worker(
    session,
    worker_user,
    team_lead_client,
    team_lead_user,
    create_task,
    create_team,
):
    task = await create_task()
    team = await create_team()

    worker_user.team_id = team["id"]
    team_lead_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    assign_response = await team_lead_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert assign_response.status_code == 200

    response = await team_lead_client.patch(f"/api/task/{task['id']}/unassign")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["user_id"] is None


async def test_team_lead_unassign_task_to_worker_in_another_team(
    session,
    worker_user,
    team_lead_client,
    team_lead_user,
    admin_client,
    create_task,
    create_team,
):
    task = await create_task()

    team = await create_team()
    team_2 = await create_team(
        name="Frontend",
        description="Frontend Team",
    )

    worker_user.team_id = team["id"]
    team_lead_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    assign_response = await admin_client.post(
        f"/api/task/{task['id']}/assign/{worker_user.id}"
    )

    assert assign_response.status_code == 200

    response = await team_lead_client.patch(f"/api/task/{task['id']}/unassign")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to unassign this task"


async def test_admin_unassign_unappointed_task(
    admin_client,
    create_task,
):
    task = await create_task()

    response = await admin_client.patch(f"/api/task/{task['id']}/unassign")

    assert response.status_code == 409

    body = response.json()

    assert body["detail"] == "Task is not assigned."


async def test_team_lead_unassign_unappointed_task_to_worker(
    session,
    worker_user,
    team_lead_client,
    team_lead_user,
    create_task,
    create_team,
):
    task = await create_task()

    team = await create_team()

    worker_user.team_id = team["id"]
    team_lead_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    response = await team_lead_client.patch(f"/api/task/{task['id']}/unassign")

    assert response.status_code == 409

    body = response.json()

    assert body["detail"] == "Task is not assigned."
