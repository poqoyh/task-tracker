from db.models import User
from db.models.user import UserRole


def can_update_user(
    current_user: User,
    target_user: User,
) -> bool:
    if current_user.id == target_user.id:
        return True

    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        if current_user.team_id is None:
            return False

        return current_user.team_id == target_user.team_id

    return False
