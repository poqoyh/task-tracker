"""create skills table

Revision ID: 864c89e7dc09
Revises: 7a5433ce107c
Create Date: 2026-06-18 14:12:15.881998

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "864c89e7dc09"
down_revision: Union[str, Sequence[str], None] = "7a5433ce107c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_skills")),
        sa.UniqueConstraint("name", name=op.f("uq_skills_name")),
    )


def downgrade() -> None:
    op.drop_table("skills")
