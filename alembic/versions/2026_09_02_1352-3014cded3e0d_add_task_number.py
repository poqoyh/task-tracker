"""add task number

Revision ID: 3014cded3e0d
Revises: facb7c910963
Create Date: 2026-09-02 13:52:19.351680

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "3014cded3e0d"
down_revision: Union[str, Sequence[str], None] = "facb7c910963"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("tasks", sa.Column("task_number", sa.Integer(), nullable=False))
    op.create_unique_constraint(
        "uq_tasks_project_id_task_number",
        "tasks",
        ["project_id", "task_number"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_tasks_project_id_task_number", "tasks", type_="unique")
    op.drop_column("tasks", "task_number")
