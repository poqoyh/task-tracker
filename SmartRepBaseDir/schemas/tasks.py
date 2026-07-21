from datetime import datetime

from pydantic import BaseModel

from db.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    name: str
    description: str
    status: TaskStatus = TaskStatus.CREATED
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    user_id: int | None = None


class TaskRead(TaskBase):
    id: int
    user_id: int | None
    created_at: datetime
