from pydantic import BaseModel, ConfigDict


class LabelBase(BaseModel):
    name: str


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    name: str | None = None


class LabelRead(LabelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
