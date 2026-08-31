from db.models import User, Project
from db.models.user import UserRole


def can_view_project(current_user: User, project: Project) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        return current_user.team_id == project.team_id

    return False


def can_manage_project(current_user: User, project: Project) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        return current_user.team_id == project.team_id

    return False
