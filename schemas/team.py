from pydantic import BaseModel, ConfigDict


class TeamBase(BaseModel):
    name: str
    description: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    name: str | None = None
    description: str | None = None


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
