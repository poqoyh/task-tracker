from db.models import User, Team
from db.models.user import UserRole


def can_view_team(current_user: User, team: Team) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        return current_user.team_id == team.id

    return False



def can_manage_team(current_user: User, team: Team) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        return current_user.team_id == team.id

    return False



def can_remove_user_from_team(current_user: User, target_user: User) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True
    if current_user.role == UserRole.TEAM_LEAD:
        if current_user.team_id is None:
            return False
        return current_user.team_id == target_user.team_id
    return False