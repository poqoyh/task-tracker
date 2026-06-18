from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from db.base import Base

from db.mixins.integer_id_pk import IntIDPKMixin


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
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
