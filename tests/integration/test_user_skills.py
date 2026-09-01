import pytest

pytest = pytest.mark.asyncio


"""
Get user skills
"""


async def test_admin_get_skills_success(
    admin_client, worker_user, create_skill, assign_skill_to_user
):
    skill = await create_skill()
    await assign_skill_to_user(worker_user.id, skill["id"])

    response = await admin_client.get(f"/api/user_skill/{worker_user.id}/skills/")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["skill"]["id"] == skill["id"]


async def test_team_lead_get_user_skills_own_team(
    team_lead_client,
    team_lead_user,
    worker_user,
    same_team,
    create_skill,
    assign_skill_to_user,
):
    await same_team(team_lead_user, worker_user)

    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    response = await team_lead_client.get(f"/api/user_skill/{worker_user.id}/skills/")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["skill"]["id"] == skill["id"]


async def test_team_lead_get_user_skill_another_team_forbidden(
    team_lead_client,
    team_lead_user,
    worker_user,
    same_team,
    create_skill,
    assign_skill_to_user,
):
    await same_team(team_lead_user, team_name="Backend")
    await same_team(worker_user, team_name="Frontend")

    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    response = await team_lead_client.get(f"/api/user_skill/{worker_user.id}/skills/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this user's skills"


async def test_worker_get_user_skill_forbidden(
    worker_client,
    worker_user,
    second_worker_user,
    create_skill,
    assign_skill_to_user,
):

    skill = await create_skill()

    await assign_skill_to_user(user_id=second_worker_user.id, skill_id=skill["id"])

    response = await worker_client.get(f"/api/user_skill/{worker_user.id}/skills/")

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to view this user's skills"


"""
Assign skill to user
"""


async def test_admin_assign_skill_to_user(
    admin_client,
    worker_user,
    create_skill,
):
    skill = await create_skill()

    response = await admin_client.post(
        f"/api/user_skill/{worker_user.id}/skills",
        json={"skill_id": skill["id"], "experience_months": 10},
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["user_skills"]) == 1

    assert body["user_skills"][0]["skill"]["id"] == skill["id"]
    assert body["user_skills"][0]["experience_months"] == 10


async def test_team_lead_assign_skill_to_user_in_same_team_success(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
):
    skill = await create_skill()

    await same_team(team_lead_user, worker_user)

    response = await team_lead_client.post(
        f"/api/user_skill/{worker_user.id}/skills",
        json={"skill_id": skill["id"], "experience_months": 10},
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["user_skills"]) == 1

    assert body["user_skills"][0]["skill"]["id"] == skill["id"]
    assert body["user_skills"][0]["experience_months"] == 10


async def test_team_lead_assign_skill_to_user_in_same_team_409(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
    assign_skill_to_user,
):
    skill = await create_skill()

    await same_team(team_lead_user, worker_user)

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    response = await team_lead_client.post(
        f"/api/user_skill/{worker_user.id}/skills",
        json={"skill_id": skill["id"], "experience_months": 10},
    )

    assert response.status_code == 409

    body = response.json()

    assert body["detail"] == "User already has this skill"


async def test_worker_assign_skill_forbidden(
    worker_client,
    worker_user,
    create_skill,
):
    skill = await create_skill()

    response = await worker_client.post(
        f"/api/user_skill/{worker_user.id}/skills",
        json={"skill_id": skill["id"], "experience_months": 10},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this user's skills"


"""
Update user skill
"""


async def test_admin_update_user_skill(
    admin_client,
    worker_user,
    assign_skill_to_user,
    create_skill,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    response = await admin_client.patch(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_skills"][0]["experience_months"] == 16


async def test_team_lead_update_user_skill_success(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
    assign_skill_to_user,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    await same_team(team_lead_user, worker_user)

    response = await team_lead_client.patch(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["user_skills"][0]["experience_months"] == 16


async def test_team_lead_update_user_skill_forbidden(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
    assign_skill_to_user,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    await same_team(team_lead_user, team_name="Backend")
    await same_team(worker_user, team_name="Frontend")

    response = await team_lead_client.patch(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this user's skills"


async def test_team_lead_update_user_skill_404(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
):
    skill = await create_skill()

    await same_team(team_lead_user, worker_user)

    response = await team_lead_client.patch(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "User doesn't have this skill."


async def test_worker_update_user_skill_forbidden(
    worker_client,
    worker_user,
    create_skill,
    assign_skill_to_user,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    response = await worker_client.patch(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this user's skills"


"""
Delete user skill
"""


async def test_admin_delete_user_skill(
    admin_client,
    worker_user,
    assign_skill_to_user,
    create_skill,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    response = await admin_client.delete(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["message"] == "Skill deleted successfully."


async def test_team_lead_delete_user_skill_success(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
    assign_skill_to_user,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    await same_team(team_lead_user, worker_user)

    response = await team_lead_client.delete(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["message"] == "Skill deleted successfully."


async def test_team_lead_delete_user_skill_forbidden(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
    assign_skill_to_user,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    await same_team(team_lead_user, team_name="Backend")
    await same_team(worker_user, team_name="Frontend")

    response = await team_lead_client.delete(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this user's skills"


async def test_team_lead_delete_user_skill_404(
    team_lead_client,
    team_lead_user,
    worker_user,
    create_skill,
    same_team,
):
    skill = await create_skill()

    await same_team(team_lead_user, worker_user)

    response = await team_lead_client.delete(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 404

    body = response.json()

    assert body["detail"] == "User doesn't have this skill."


async def test_worker_delete_user_skill_forbidden(
    worker_client,
    worker_user,
    create_skill,
    assign_skill_to_user,
):
    skill = await create_skill()

    await assign_skill_to_user(user_id=worker_user.id, skill_id=skill["id"])

    response = await worker_client.delete(
        f"/api/user_skill/{worker_user.id}/skills/{skill['id']}",
        params={"new_experience": 16},
    )

    assert response.status_code == 403

    body = response.json()

    assert body["detail"] == "Not enough permissions to manage this user's skills"
