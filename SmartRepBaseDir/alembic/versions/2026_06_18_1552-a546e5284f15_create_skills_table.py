"""create skills table

Revision ID: a546e5284f15
Revises: 2e92aa7d7d13
Create Date: 2026-06-18 15:52:46.688750

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a546e5284f15"
down_revision: Union[str, Sequence[str], None] = "2e92aa7d7d13"
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
