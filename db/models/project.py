from datetime import datetime

from sqlalchemy import String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins.integer_id_pk import IntIDPKMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.team import Team
    from db.models.task import Task


class Project(IntIDPKMixin, Base):
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    key: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    team: Mapped["Team"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")
