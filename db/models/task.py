from datetime import datetime

from sqlalchemy import String, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins.integer_id_pk import IntIDPKMixin

from typing import TYPE_CHECKING

from enum import Enum
from sqlalchemy import Enum as SQLEnum


class TaskStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


if TYPE_CHECKING:
    from db.models.user import User
    from db.models.project import Project


class Task(IntIDPKMixin, Base):
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "task_number",
            name="uq_tasks_project_id_task_number",
        ),
    )

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)

    task_number: Mapped[int] = mapped_column(nullable=False)

    parent_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=True,
    )

    @property
    def human_id(self) -> str:
        return f"{self.project.key}-{self.task_number}"

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(
            TaskStatus,
            values_callable=lambda enum: [item.value for item in enum],
            name="taskstatus",
        ),
        default=TaskStatus.CREATED,
        nullable=False,
    )

    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(
            TaskPriority,
            values_callable=lambda enum: [item.value for item in enum],
            name="taskpriority",
        ),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    user: Mapped["User"] = relationship(back_populates="tasks")

    project: Mapped["Project"] = relationship(back_populates="tasks")

    parent_task: Mapped["Task | None"] = relationship(
        remote_side="Task.id",
        back_populates="subtasks",
    )

    subtasks: Mapped[list["Task"]] = relationship(
        back_populates="parent_task",
    )
