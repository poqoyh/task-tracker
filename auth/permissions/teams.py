from db.models import User, Team
from db.models.user import UserRole


def can_view_team(current_user: User, team: Team) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role == UserRole.TEAM_LEAD:
        return current_user.team_id == team.id

    return False