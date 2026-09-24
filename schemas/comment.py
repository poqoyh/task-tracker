from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from schemas.user import UserShortRead


class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1024)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=1024)


class CommentRead(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    edited_at: datetime | None
    task_id: int
    user: UserShortRead
