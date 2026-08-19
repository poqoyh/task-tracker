from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins.integer_id_pk import IntIDPKMixin


class Skill(IntIDPKMixin, Base):
    name: Mapped[str] = mapped_column(
        String(256),
        unique=True,
        nullable=False,
    )

    user_skills = relationship(
        "UserSkill",
        back_populates="skill",
    )
