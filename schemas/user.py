from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from db.models.user import UserRole
from schemas.tasks import TaskRead
from schemas.team import TeamRead
from schemas.user_skill import UserSkillRead


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


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
