from db.models import (
    User,
    Task,
)
from db.models.task import TaskStatus
from db.models.user import UserRole

"""
get_task, update_task,unassign_task
"""


def can_manage_task(
    current_user: User,
    task: Task,
) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        if current_user.team_id is None or task.project_id is None:
            return False
        return current_user.team_id == task.project.team_id
    return False


"""
get_user_tasks"""


def can_view_tasks(
    current_user: User,
    target_user: User,
) -> bool:

    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        if current_user.team_id is None:
            return False

        return current_user.team_id == target_user.team_id

    if current_user.role == UserRole.WORKER:
        return current_user.id == target_user.id

    return False


"""
assign_task_to_user
"""


def can_assign_task(
    current_user: User,
    target_user: User,
) -> bool:

    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        if current_user.team_id is None:
            return False

        return current_user.team_id == target_user.team_id

    return False


"""
Update task status
"""
ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.CREATED: {TaskStatus.IN_PROGRESS},
    TaskStatus.IN_PROGRESS: {TaskStatus.REVIEW, TaskStatus.CREATED},
    TaskStatus.REVIEW: {TaskStatus.DONE, TaskStatus.IN_PROGRESS},
    TaskStatus.DONE: {TaskStatus.IN_PROGRESS},  # explicit "reopen", not to CREATED
}


def validate_status_transition(old: TaskStatus, new: TaskStatus) -> bool:
    if old == new:
        return True
    return new in ALLOWED_TRANSITIONS.get(old, set())
