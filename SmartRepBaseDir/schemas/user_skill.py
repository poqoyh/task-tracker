from pydantic import BaseModel

from schemas.skill import SkillShortRead


class UserSkillCreate(BaseModel):
    skill_id: int
    experience_months: int


class UserSkillRead(BaseModel):
    skill: SkillShortRead
    experience_months: int


class UserSkillUpdate(BaseModel):
    experience_months: int
