from db.models import (
    User,
    Task,
)
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
        if current_user.team_id is None:
            return False

        if task.user is None:
            return False

        return current_user.team_id == task.user.team_id

    return False
