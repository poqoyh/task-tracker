import pytest

"""
Create label
"""


async def test_create_label_admin_success(admin_client):
    response = await admin_client.post(
        "/api/labels/",
        json={"name": "backend"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == 1
    assert body["name"] == "backend"


async def test_create_label_team_lead_success(team_lead_client):
    response = await team_lead_client.post(
        "/api/labels/",
        json={"name": "backend"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "backend"


async def test_create_label_worker_forbidden(worker_client):
    response = await worker_client.post(
        "/api/labels/",
        json={"name": "backend"},
    )

    assert response.status_code == 403


async def test_create_label_unauthenticated(client):
    response = await client.post(
        "/api/labels/",
        json={"name": "backend"},
    )

    assert response.status_code == 401


async def test_create_label_duplicate_409(
    admin_client,
    create_label,
):
    await create_label("backend")

    response = await admin_client.post(
        "/api/labels/",
        json={"name": "backend"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Label with this name is already create"


"""
Get labels
"""


async def test_get_labels_success(
    admin_client,
    create_label,
):
    await create_label("backend")
    await create_label("frontend")

    response = await admin_client.get("/api/labels/")

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["name"] == "backend"
    assert body["items"][1]["name"] == "frontend"


async def test_get_labels_pagination(
    admin_client,
    create_label,
):
    await create_label("backend")
    await create_label("frontend")
    await create_label("devops")

    response = await admin_client.get(
        "/api/labels/",
        params={
            "limit": 1,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["limit"] == 1
    assert body["offset"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["name"] == "frontend"


async def test_get_labels_worker_forbidden(worker_client):
    response = await worker_client.get("/api/labels/")

    assert response.status_code == 403


"""
Get label by id
"""


async def test_get_label_by_id_success(
    admin_client,
    create_label,
):
    label = await create_label()

    response = await admin_client.get(f"/api/labels/{label['id']}/")

    assert response.status_code == 200
    assert response.json() == label


async def test_get_label_by_id_404(admin_client):
    response = await admin_client.get("/api/labels/999/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


async def test_get_label_by_id_worker_forbidden(
    worker_client,
    create_label,
):
    label = await create_label()

    response = await worker_client.get(f"/api/labels/{label['id']}/")

    assert response.status_code == 403


"""
Update label
"""


async def test_update_label_success(
    admin_client,
    create_label,
):
    label = await create_label()

    response = await admin_client.patch(
        f"/api/labels/{label['id']}/",
        json={"name": "backend-api"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "backend-api"


async def test_update_label_team_lead_success(
    team_lead_client,
    create_label,
):
    label = await create_label()

    response = await team_lead_client.patch(
        f"/api/labels/{label['id']}/",
        json={"name": "backend-api"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "backend-api"


async def test_update_label_duplicate_409(
    admin_client,
    create_label,
):
    first = await create_label("backend")
    await create_label("frontend")

    response = await admin_client.patch(
        f"/api/labels/{first['id']}/",
        json={"name": "frontend"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("Label with this name already exists")


async def test_update_label_404(admin_client):
    response = await admin_client.patch(
        "/api/labels/999/",
        json={"name": "backend"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


async def test_update_label_worker_forbidden(
    worker_client,
    create_label,
):
    label = await create_label()

    response = await worker_client.patch(
        f"/api/labels/{label['id']}/",
        json={"name": "backend-api"},
    )

    assert response.status_code == 403


"""
Delete label
"""


async def test_delete_label_success(
    admin_client,
    create_label,
):
    label = await create_label()

    response = await admin_client.delete(f"/api/labels/{label['id']}/")

    assert response.status_code == 200

    assert response.json()["message"] == ("Label deleted successfully")

    get_response = await admin_client.get(f"/api/labels/{label['id']}/")

    assert get_response.status_code == 404


async def test_delete_label_404(admin_client):
    response = await admin_client.delete("/api/labels/999/")

    assert response.status_code == 404
    assert response.json()["detail"] == "Label not found"


async def test_delete_label_worker_forbidden(
    worker_client,
    create_label,
):
    label = await create_label()

    response = await worker_client.delete(f"/api/labels/{label['id']}/")

    assert response.status_code == 403


async def test_delete_label_with_tasks_409(
    admin_client,
    create_label,
    create_task,
    create_team,
    create_project,
):
    label = await create_label()

    team = await create_team()
    project = await create_project(team_id=team["id"])

    task = await create_task(project_id=project["id"])

    add_response = await admin_client.post(
        f"/api/task/{task['id']}/add_label/{label['id']}"
    )

    assert add_response.status_code == 200

    response = await admin_client.delete(f"/api/labels/{label['id']}/")

    assert response.status_code == 409
    assert response.json()["detail"] == ("Label has tasks, cannot delete")
