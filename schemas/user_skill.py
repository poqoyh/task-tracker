from pydantic import BaseModel, Field

from schemas.skill import SkillShortRead


class UserSkillCreate(BaseModel):
    skill_id: int
    experience_months: int = Field(ge=0)


class UserSkillRead(BaseModel):
    skill: SkillShortRead
    experience_months: int


class UserSkillUpdate(BaseModel):
    experience_months: int = Field(ge=0)
