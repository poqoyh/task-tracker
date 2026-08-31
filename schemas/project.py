from datetime import datetime

from pydantic import BaseModel, field_validator, ConfigDict


class ProjectBase(BaseModel):
    name: str
    key: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    team_id: int

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        v = v.strip().upper()

        if not (2 <= len(v) <= 10):
            raise ValueError("Key must be 2-10 characters")
        if not v.isalpha():
            raise ValueError("Key must contain only letters")
        return v


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    created_at: datetime
