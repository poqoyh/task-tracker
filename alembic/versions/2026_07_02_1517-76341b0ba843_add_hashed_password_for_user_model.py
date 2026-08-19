"""Add hashed_password for user model

Revision ID: 76341b0ba843
Revises: f9d8e84cef81
Create Date: 2026-07-02 15:17:52.537720

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "76341b0ba843"
down_revision: Union[str, Sequence[str], None] = "f9d8e84cef81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.String(length=256), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
