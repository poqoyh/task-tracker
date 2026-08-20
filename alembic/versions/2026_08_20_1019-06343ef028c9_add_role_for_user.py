"""add role for user

Revision ID: 06343ef028c9
Revises: 76341b0ba843
Create Date: 2026-08-20 10:19:33.216440

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "06343ef028c9"
down_revision: Union[str, Sequence[str], None] = "76341b0ba843"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role = sa.Enum("worker", "team_lead", "admin", name="userrole")
    user_role.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role,
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
