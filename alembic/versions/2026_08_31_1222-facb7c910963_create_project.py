"""create project

Revision ID: facb7c910963
Revises: 06343ef028c9
Create Date: 2026-08-31 12:22:09.558891

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "facb7c910963"
down_revision: Union[str, Sequence[str], None] = "06343ef028c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "projects",
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("key", sa.String(length=10), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["team_id"], ["teams.id"], name=op.f("fk_projects_team_id_teams")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_projects")),
        sa.UniqueConstraint("key", name=op.f("uq_projects_key")),
    )
    op.add_column("tasks", sa.Column("project_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        op.f("fk_tasks_project_id_projects"),
        "tasks",
        "projects",
        ["project_id"],
        ["id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("fk_tasks_project_id_projects"), "tasks", type_="foreignkey"
    )
    op.drop_column("tasks", "project_id")
    op.drop_table("projects")
