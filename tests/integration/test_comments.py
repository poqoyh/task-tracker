import pytest

pytest = pytest.mark.asyncio


"""
Create comment tests
"""


async def test_create_comment_unauthenticated(
    client, create_task, create_team, create_project
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    response = await client.post(f"/api/comments/tasks/{task['id']}/comments")

    assert response.status_code == 401


async def test_admin_create_comment_success(
    admin_client, create_task, create_team, create_project
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    response = await admin_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Test comment"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["text"] == "Test comment"
    assert body["task_id"] == task["id"]


async def test_team_lead_create_comment_in_own_team_success(
    session,
    team_lead_client,
    team_lead_user,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    team_lead_user.team_id = team["id"]
    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    response = await team_lead_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Test comment"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["text"] == "Test comment"


async def test_team_lead_create_comment_in_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend team")

    team_lead_user.team_id = team["id"]
    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team_2["id"])
    task = await create_task(project_id=project["id"])

    response = await team_lead_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Test comment"},
    )

    assert response.status_code == 403

    body = response.json()
    assert body["detail"] == "Not enough permissions to create comment on this task"


async def test_worker_create_comment_assigned_to_task_success(
    session,
    worker_client,
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

    response = await worker_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Test comment"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["text"] == "Test comment"


async def test_worker_create_comment_in_same_team_success(
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
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Test comment"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["text"] == "Test comment"


async def test_worker_create_comment_not_assigned_not_in_team_forbidden(
    session,
    worker_client,
    worker_user,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend team")

    worker_user.team_id = team["id"]
    session.add(worker_user)
    await session.commit()

    project = await create_project(team_id=team_2["id"])
    task = await create_task(project_id=project["id"])

    response = await worker_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Test comment"},
    )

    assert response.status_code == 403

    body = response.json()
    assert body["detail"] == "Not enough permissions to create comment on this task"


async def test_create_comment_task_not_found(
    admin_client,
):
    response = await admin_client.post(
        "/api/comments/tasks/999/comments",
        json={"text": "Test comment"},
    )

    assert response.status_code == 404

    body = response.json()
    assert body["detail"] == "Task not found."


"""
Get task comments tests
"""


async def test_get_task_comments_unauthenticated(
    client, create_task, create_team, create_project
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    response = await client.get(f"/api/comments/tasks/{task['id']}/comments")

    assert response.status_code == 401


async def test_get_task_comments_success(
    admin_client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    await create_comment(task_id=task["id"], text="First comment")
    await create_comment(task_id=task["id"], text="Second comment")

    response = await admin_client.get(f"/api/comments/tasks/{task['id']}/comments")

    assert response.status_code == 200

    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_get_task_comments_task_not_found(
    admin_client,
):
    response = await admin_client.get("/api/comments/tasks/999/comments")

    assert response.status_code == 404

    body = response.json()
    assert body["detail"] == "Task not found."


"""
Get comment by id tests
"""


async def test_get_comment_by_id_unauthenticated(
    client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])
    comment = await create_comment(task_id=task["id"])

    response = await client.get(f"/api/comments/comments/{comment['id']}")

    assert response.status_code == 401


async def test_get_comment_by_id_success(
    admin_client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])
    comment = await create_comment(task_id=task["id"])

    response = await admin_client.get(f"/api/comments/comments/{comment['id']}")

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == comment["id"]
    assert body["text"] == "Test comment"


async def test_get_comment_by_id_not_found(
    admin_client,
):
    response = await admin_client.get("/api/comments/comments/999")

    assert response.status_code == 404

    body = response.json()
    assert body["detail"] == "Comment not found."


"""
Update comment tests
"""


async def test_update_comment_unauthenticated(
    client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])
    comment = await create_comment(task_id=task["id"])

    response = await client.patch(
        f"/api/comments/comments/{comment['id']}",
        json={"text": "Updated comment"},
    )

    assert response.status_code == 401


async def test_admin_update_comment_success(
    admin_client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])
    comment = await create_comment(task_id=task["id"])

    response = await admin_client.patch(
        f"/api/comments/comments/{comment['id']}",
        json={"text": "Updated comment"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["text"] == "Updated comment"
    assert body["edited_at"] is not None


async def test_team_lead_update_comment_in_own_team_success(
    session,
    team_lead_client,
    team_lead_user,
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    team_lead_user.team_id = team["id"]
    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    # Create comment as team_lead
    create_response = await team_lead_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )
    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    response = await team_lead_client.patch(
        f"/api/comments/comments/{comment_id}",
        json={"text": "Updated comment"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["text"] == "Updated comment"


async def test_team_lead_update_comment_in_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend team")

    team_lead_user.team_id = team["id"]
    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team_2["id"])
    task = await create_task(project_id=project["id"])

    # Create comment as admin (in team_2)
    create_response = await admin_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )
    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    response = await team_lead_client.patch(
        f"/api/comments/comments/{comment_id}",
        json={"text": "Updated comment"},
    )

    assert response.status_code == 403

    body = response.json()
    assert body["detail"] == "Not enough permissions to update this comment"


async def test_worker_update_own_comment_success(
    session,
    worker_client,
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

    create_response = await worker_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )

    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    response = await worker_client.patch(
        f"/api/comments/comments/{comment_id}",
        json={"text": "Updated comment"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["text"] == "Updated comment"


async def test_worker_update_other_comment_forbidden(
    session,
    worker_client,
    worker_user,
    second_worker_user,
    admin_client,
    authenticated_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    worker_user.team_id = team["id"]
    second_worker_user.team_id = team["id"]
    session.add_all([worker_user, second_worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    # Create comment as first worker
    create_response = await worker_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )

    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    # Try to update as second worker
    second_worker_client = authenticated_client(second_worker_user)

    response = await second_worker_client.patch(
        f"/api/comments/comments/{comment_id}",
        json={"text": "Updated comment"},
    )

    assert response.status_code == 403

    body = response.json()
    assert body["detail"] == "Not enough permissions to update this comment"


async def test_update_comment_not_found(
    admin_client,
):
    response = await admin_client.patch(
        "/api/comments/comments/999",
        json={"text": "Updated comment"},
    )

    assert response.status_code == 404

    body = response.json()
    assert body["detail"] == "Comment not found."


async def test_update_comment_no_fields_400(
    admin_client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])
    comment = await create_comment(task_id=task["id"])

    response = await admin_client.patch(
        f"/api/comments/comments/{comment['id']}",
        json={},
    )

    assert response.status_code == 400

    body = response.json()
    assert body["detail"] == "No fields to update"


"""
Delete comment tests
"""


async def test_delete_comment_unauthenticated(
    client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])
    comment = await create_comment(task_id=task["id"])

    response = await client.delete(f"/api/comments/comments/{comment['id']}")

    assert response.status_code == 401


async def test_admin_delete_comment_success(
    admin_client, create_task, create_team, create_project, create_comment
):
    team = await create_team()
    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])
    comment = await create_comment(task_id=task["id"])

    response = await admin_client.delete(f"/api/comments/comments/{comment['id']}")

    assert response.status_code == 200


async def test_team_lead_delete_comment_in_own_team_success(
    session,
    team_lead_client,
    team_lead_user,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    team_lead_user.team_id = team["id"]
    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    # Create comment as team_lead
    create_response = await team_lead_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )
    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    response = await team_lead_client.delete(f"/api/comments/comments/{comment_id}")

    assert response.status_code == 200


async def test_team_lead_delete_comment_in_another_team_forbidden(
    session,
    team_lead_client,
    team_lead_user,
    admin_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    team_2 = await create_team(name="Frontend", description="Frontend team")

    team_lead_user.team_id = team["id"]
    session.add(team_lead_user)
    await session.commit()

    project = await create_project(team_id=team_2["id"])
    task = await create_task(project_id=project["id"])

    # Create comment as admin (in team_2)
    create_response = await admin_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )
    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    response = await team_lead_client.delete(f"/api/comments/comments/{comment_id}")

    assert response.status_code == 403

    body = response.json()
    assert body["detail"] == "Not enough permissions to delete this comment"


async def test_worker_delete_own_comment_success(
    session,
    worker_client,
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

    create_response = await worker_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )

    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    response = await worker_client.delete(f"/api/comments/comments/{comment_id}")

    assert response.status_code == 200


async def test_worker_delete_other_comment_forbidden(
    session,
    worker_client,
    worker_user,
    second_worker_user,
    admin_client,
    authenticated_client,
    create_task,
    create_team,
    create_project,
):
    team = await create_team()
    worker_user.team_id = team["id"]
    second_worker_user.team_id = team["id"]
    session.add_all([worker_user, second_worker_user])
    await session.commit()

    project = await create_project(team_id=team["id"])
    task = await create_task(project_id=project["id"])

    await admin_client.post(f"/api/task/{task['id']}/assign/{worker_user.id}")

    # Create comment as first worker
    create_response = await worker_client.post(
        f"/api/comments/tasks/{task['id']}/comments",
        json={"text": "Original comment"},
    )

    assert create_response.status_code == 200
    comment_id = create_response.json()["id"]

    # Try to delete as second worker
    second_worker_client = authenticated_client(second_worker_user)

    response = await second_worker_client.delete(
        f"/api/comments/comments/{comment_id}"
    )

    assert response.status_code == 403

    body = response.json()
    assert body["detail"] == "Not enough permissions to delete this comment"


async def test_delete_comment_not_found(
    admin_client,
):
    response = await admin_client.delete("/api/comments/comments/999")

    assert response.status_code == 404

    body = response.json()
    assert body["detail"] == "Comment not found."
