from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Skill(Base):
    name: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        nullable=False,
    )
