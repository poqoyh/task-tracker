from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    name: str


class SkillCreate(SkillBase):
    pass


class SkillUpdate(SkillBase):
    name: str | None = None


class SkillShortRead(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
