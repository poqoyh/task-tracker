from db.models import User, Comment
from db.models.user import UserRole


def can_create_comment(
    current_user: User,
    task_user_id: int | None,
    task_team_id: int,
) -> bool:

    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        return current_user.team_id == task_team_id

    if current_user.role == UserRole.WORKER:
        if current_user.team_id == task_team_id:
            return True
        if task_user_id == current_user.id:
            return True

    return False


def can_manage_comment(
    current_user: User,
    comment: Comment,
) -> bool:

    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        if current_user.team_id is None or comment.task.project.team_id is None:
            return False
        return current_user.team_id == comment.task.project.team_id

    if current_user.role == UserRole.WORKER:
        return current_user.id == comment.user_id

    return False
