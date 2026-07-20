from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str
    description: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    name: str | None = None
    description: str | None = None


class TeamRead(TeamBase):
    id: int
