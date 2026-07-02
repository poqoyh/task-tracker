from sqlalchemy import String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from db.base import Base

from db.mixins.integer_id_pk import IntIDPKMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.team import Team
    from db.models.task import Task


class User(IntIDPKMixin, Base):
    email: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )

    user_skills = relationship(
        "UserSkill",
        back_populates="user",
    )

    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
    )
    team: Mapped["Team"] = relationship(back_populates="users")

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
