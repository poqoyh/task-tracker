"""create user skills table

Revision ID: 77e8cb398731
Revises: a546e5284f15
Create Date: 2026-06-19 16:18:13.174681

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "77e8cb398731"
down_revision: Union[str, Sequence[str], None] = "a546e5284f15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_skills",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("experience_months", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.id"],
            name=op.f("fk_user_skills_skill_id_skills"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_skills_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("user_id", "skill_id", name=op.f("pk_user_skills")),
    )


def downgrade() -> None:
    op.drop_table("user_skills")
