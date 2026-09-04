"""add parent_task_id to tasks

Revision ID: ba28a6c333eb
Revises: 3014cded3e0d
Create Date: 2026-09-04 14:59:13.793585

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ba28a6c333eb"
down_revision: Union[str, Sequence[str], None] = "3014cded3e0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("tasks", sa.Column("parent_task_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        op.f("fk_tasks_parent_task_id_tasks"),
        "tasks",
        "tasks",
        ["parent_task_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_tasks_parent_task_id_tasks"), "tasks", type_="foreignkey"
    )
    op.drop_column("tasks", "parent_task_id")
