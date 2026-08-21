import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

from db.models.user import UserRole
from schemas.tasks import TaskRead
from schemas.team import TeamRead
from schemas.user_skill import UserSkillRead


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be least 8 characters long")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[@_-]", value):
            raise ValueError(
                "Password must contain at least one special character (@,-, _)"
            )

        return value


class UserLogin(BaseModel):
    identifier: str
    password: str


class UserShortRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    created_at: datetime


class UserReadWithSkills(BaseModel):
    username: str
    role: UserRole
    user_skills: list[UserSkillRead]


class UserReadWithTeam(BaseModel):
    username: str
    role: UserRole
    team: TeamRead | None


class UserProfileRead(UserBase):
    created_at: datetime
    user_skills: list[UserSkillRead]
    team: TeamRead | None
    tasks: list[TaskRead]


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
