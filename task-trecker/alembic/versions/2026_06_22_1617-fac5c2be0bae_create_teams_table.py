"""create teams table

Revision ID: fac5c2be0bae
Revises: 77e8cb398731
Create Date: 2026-06-22 16:17:34.458259

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "fac5c2be0bae"
down_revision: Union[str, Sequence[str], None] = "77e8cb398731"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "teams",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_teams")),
        sa.UniqueConstraint("name", name=op.f("uq_teams_name")),
    )


def downgrade() -> None:
    op.drop_table("teams")
