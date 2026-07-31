from datetime import datetime

from sqlalchemy import String, func, ForeignKey
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


class Task(IntIDPKMixin, Base):
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
