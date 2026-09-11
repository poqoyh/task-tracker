from sqlalchemy import (
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class TaskLabel(Base):
    __table_args__ = (
        PrimaryKeyConstraint(
            "label_id",
            "task_id",
        ),
    )

    label_id: Mapped[int] = mapped_column(
        ForeignKey("labels.id"),
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
    )
