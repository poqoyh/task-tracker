from datetime import datetime

from sqlalchemy import String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins.integer_id_pk import IntIDPKMixin

from typing import TYPE_CHECKING

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

    status: Mapped[str] = mapped_column(
        String(32),
        default="created",
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
