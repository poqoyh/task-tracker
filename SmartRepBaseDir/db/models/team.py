from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from db.mixins.integer_id_pk import IntIDPKMixin


class Team(IntIDPKMixin, Base):
    name: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
