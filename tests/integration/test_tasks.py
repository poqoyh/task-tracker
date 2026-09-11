import pytest

pytest = pytest.mark.asyncio


"""
Get task by id
"""


async def test_get_task_by_id_unauthenticated(
    client, create_task, create_team, create_project
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    response = await client.get(f"/api/task/{task['id']}")

    assert response.status_code == 401


async def test_get_task_by_id_worker_forbidden(
    worker_client, create_task, create_team, create_project
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    response = await worker_client.get(f"/api/task/{task['id']}")

    assert response.status_code == 403


"""
Get Users Tasks 
"""


async def test_worker_get_himself_tasks_success(
    worker_client,
    worker_user,
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

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
    create_team,
    create_project,
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

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
    create_project,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

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
    create_project,
):
    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

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
    create_project,
    create_team,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

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
    create_project,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):
    team = await create_team()

    team_2 = await create_team(
        name="Frontend",
        description="Frontend team",
    )

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team_2["id"])
    task = await create_task(project_id=project["id"])

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    response = await team_lead_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to update this task"


async def test_team_lead_update_unassigned_task_in_own_project_success(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
    create_task,
    create_project,
):

    team = await create_team()

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    response = await team_lead_client.patch(
        f"/api/task/{task["id"]}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )

    assert response.status_code == 200


async def test_team_lead_update_unassigned_task_in_another_project_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    create_team,
    create_task,
    create_project,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend team")

    team_lead_user.team_id = team["id"]

    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team_2["id"])

    task = await create_task(project_id=project["id"])

    response = await team_lead_client.patch(
        f"/api/task/{task['id']}",
        json={"name": "Updated Task Name", "description": "Updated Task Description"},
    )
    assert response.status_code == 403


async def test_team_lead_without_team_update_task(
    session,
    team_lead_client,
    team_lead_user,
    worker_user,
    admin_client,
    create_team,
    create_task,
    create_project,
):
    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

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
    create_project,
):
    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

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
    session,
    worker_user,
    admin_client,
    create_task,
    create_project,
    create_team,
):
    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):
    team = await create_team()

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):

    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend Team")

    team_lead_user.team_id = team["id"]
    worker_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):

    team = await create_team()

    worker_user.team_id = team["id"]

    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):
    team = await create_team()

    worker_user.team_id = team["id"]
    team_lead_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):

    team = await create_team()
    team_2 = await create_team(
        name="Frontend",
        description="Frontend Team",
    )

    worker_user.team_id = team["id"]
    team_lead_user.team_id = team_2["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
    create_team,
):
    team = await create_team()
    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

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
    create_project,
):

    team = await create_team()

    worker_user.team_id = team["id"]
    team_lead_user.team_id = team["id"]

    session.add_all([team_lead_user, worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    response = await team_lead_client.patch(f"/api/task/{task['id']}/unassign")

    assert response.status_code == 409

    body = response.json()

    assert body["detail"] == "Task is not assigned."


"""
SUBTASK
"""


async def test_create_subtask_success(
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    project = await create_project(team_id=team["id"])

    parent = await create_task(project_id=project["id"])

    response = await admin_client.post(
        "/api/task/",
        json={
            "name": "Child task",
            "project_id": project["id"],
            "parent_task_id": parent["id"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "Child task"
    assert body["project_id"] == project["id"]


async def test_create_subtask_parent_from_another_project_409(
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()

    project_a = await create_project(
        team_id=team["id"],
        key="AAA",
    )

    project_b = await create_project(
        team_id=team["id"],
        key="BBB",
        name="Second project",
    )

    parent = await create_task(project_id=project_a["id"])

    response = await admin_client.post(
        "/api/task/",
        json={
            "name": "Invalid child",
            "project_id": project_b["id"],
            "parent_task_id": parent["id"],
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == ("Parent task must belong to the same project")


async def test_create_subtask_parent_not_found(
    admin_client,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    response = await admin_client.post(
        "/api/task/",
        json={
            "name": "Invalid child",
            "project_id": project["id"],
            "parent_task_id": 999,
        },
    )

    assert response.status_code == 404


async def test_parent_cannot_be_done_with_unfinished_subtask(
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    parent = await create_task(project_id=project["id"])

    child_response = await admin_client.post(
        "/api/task/",
        json={
            "name": "Child task",
            "project_id": project["id"],
            "parent_task_id": parent["id"],
        },
    )

    assert child_response.status_code == 200

    await admin_client.patch(
        f"/api/task/{parent['id']}",
        json={"status": "in_progress"},
    )

    await admin_client.patch(
        f"/api/task/{parent['id']}",
        json={"status": "review"},
    )

    response = await admin_client.patch(
        f"/api/task/{parent['id']}",
        json={"status": "done"},
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Cannot complete task while it has unfinished subtasks"
    )


async def test_parent_can_be_done_when_all_subtasks_done(
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    parent = await create_task(project_id=project["id"])

    child_response = await admin_client.post(
        "/api/task/",
        json={
            "name": "Child task",
            "project_id": project["id"],
            "parent_task_id": parent["id"],
        },
    )

    assert child_response.status_code == 200

    child_id = child_response.json()["id"]

    await admin_client.patch(
        f"/api/task/{child_id}",
        json={"status": "in_progress"},
    )

    await admin_client.patch(
        f"/api/task/{child_id}",
        json={"status": "review"},
    )

    response = await admin_client.patch(
        f"/api/task/{child_id}",
        json={"status": "done"},
    )

    assert response.status_code == 200

    await admin_client.patch(
        f"/api/task/{parent['id']}",
        json={"status": "in_progress"},
    )

    await admin_client.patch(
        f"/api/task/{parent['id']}",
        json={"status": "review"},
    )

    response = await admin_client.patch(
        f"/api/task/{parent['id']}",
        json={"status": "done"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


async def test_add_label_to_task_success(
    admin_client,
    create_task,
    create_label,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    label = await create_label()

    response = await admin_client.post(
        f"/api/task/{task['id']}/add_label/{label['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == task["id"]


async def test_add_same_label_to_task_409(
    admin_client,
    create_task,
    create_label,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    label = await create_label()

    response = await admin_client.post(
        f"/api/task/{task['id']}/add_label/{label['id']}"
    )

    assert response.status_code == 200

    response = await admin_client.post(
        f"/api/task/{task['id']}/add_label/{label['id']}"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("Label already added to this task.")


async def test_add_nonexistent_label_to_task_404(
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    response = await admin_client.post(f"/api/task/{task['id']}/add_label/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


async def test_remove_label_from_task_success(
    admin_client,
    create_task,
    create_label,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    label = await create_label()

    await admin_client.post(f"/api/task/{task['id']}/add_label/{label['id']}")

    response = await admin_client.delete(
        f"/api/task/{task['id']}/remove_label/{label['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == task["id"]


async def test_remove_label_not_attached_404(
    admin_client,
    create_task,
    create_label,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    label = await create_label()

    response = await admin_client.delete(
        f"/api/task/{task['id']}/remove_label/{label['id']}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == ("Task doesn't have this label")


async def test_worker_add_label_to_task_forbidden(
    worker_client,
    create_task,
    create_label,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    label = await create_label()

    response = await worker_client.post(
        f"/api/task/{task['id']}/add_label/{label['id']}"
    )

    assert response.status_code == 403


async def test_worker_remove_label_from_task_forbidden(
    worker_client,
    create_task,
    create_label,
    create_team,
    create_project,
):
    team = await create_team()

    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    label = await create_label()

    response = await worker_client.delete(
        f"/api/task/{task['id']}/remove_label/{label['id']}"
    )

    assert response.status_code == 403
