from datetime import datetime

from pydantic import BaseModel, EmailStr

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
    id: int
    created_at: datetime


class UserReadWithSkills(BaseModel):
    username: str
    user_skills: list[UserSkillRead]


class UserReadWithTeam(BaseModel):
    username: str
    team: TeamRead | None


class UserProfileRead(UserBase):
    created_at: datetime
    user_skills: list[UserSkillRead]
    team: TeamRead | None
    tasks: list[TaskRead]


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
