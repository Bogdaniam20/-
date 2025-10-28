from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_time: str | None = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    completed: bool | None = None
    notified_60: bool | None = None
    notified_5: bool | None = None

class Task(TaskBase):
    id: int
    completed: bool
    notified_60: bool | None = None
    notified_5: bool | None = None

    class Config:
        from_attributes = True
