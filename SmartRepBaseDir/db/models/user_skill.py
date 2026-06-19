from sqlalchemy import (
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class UserSkill(Base):
    __table_args__ = (
        PrimaryKeyConstraint(
            "user_id",
            "skill_id",
        ),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"))

    experience_months: Mapped[int] = mapped_column(
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="user_skills",
    )

    skill = relationship(
        "Skill",
        back_populates="user_skills",
    )
