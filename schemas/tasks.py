from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from db.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    name: str
    description: str | None = None
    status: TaskStatus = TaskStatus.CREATED
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    project_id: int
    parent_task_id: int | None = None


class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    task_number: int
    human_id: str
    user_id: int | None
    created_at: datetime
    subtasks: list["TaskRead"] = Field(default_factory=list)


TaskRead.model_rebuild()
