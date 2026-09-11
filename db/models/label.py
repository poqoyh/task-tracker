from db.base import Base
from db.mixins.integer_id_pk import IntIDPKMixin

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.models.task import Task


class Label(IntIDPKMixin, Base):
    name: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    tasks: Mapped[list["Task"]] = relationship(
        secondary="task_labels",
        back_populates="labels",
    )
