"""add labels and task labels

Revision ID: 3e872278a64d
Revises: ba28a6c333eb
Create Date: 2026-09-08 16:07:09.488765

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "3e872278a64d"
down_revision: Union[str, Sequence[str], None] = "ba28a6c333eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "labels",
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_labels")),
        sa.UniqueConstraint("name", name=op.f("uq_labels_name")),
    )
    op.create_table(
        "task_labels",
        sa.Column("label_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["label_id"],
            ["labels.id"],
            name=op.f("fk_task_labels_label_id_labels"),
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_task_labels_task_id_tasks"),
        ),
        sa.PrimaryKeyConstraint("label_id", "task_id", name=op.f("pk_task_labels")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("task_labels")
    op.drop_table("labels")
