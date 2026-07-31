from datetime import datetime

from pydantic import BaseModel, EmailStr

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


class UserReadWithSkills(UserBase):
    username: str
    user_skills: list[UserSkillRead]


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
