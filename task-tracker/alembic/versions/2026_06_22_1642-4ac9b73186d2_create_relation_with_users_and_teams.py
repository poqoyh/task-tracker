"""create relation with users and teams

Revision ID: 4ac9b73186d2
Revises: fac5c2be0bae
Create Date: 2026-06-22 16:42:57.961964

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "4ac9b73186d2"
down_revision: Union[str, Sequence[str], None] = "fac5c2be0bae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column("users", sa.Column("team_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_users_team_id_teams"), "users", "teams", ["team_id"], ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("fk_users_team_id_teams"), "users", type_="foreignkey")
    op.drop_column("users", "team_id")
