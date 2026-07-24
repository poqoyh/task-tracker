from pydantic import BaseModel


class SkillBase(BaseModel):
    name: str


class SkillCreate(SkillBase):
    pass


class SkillUpdate(SkillBase):
    name: str | None = None


class SkillShortRead(SkillBase):
    id: int
