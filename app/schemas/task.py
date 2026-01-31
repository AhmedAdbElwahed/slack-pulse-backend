from sqlmodel import SQLModel
from typing import Optional


# Shared properties
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    column_id: int
    order: int = 0


# Properties to receive on creation
class TaskCreate(TaskBase):
    pass


# Properties to receive on update (all optional)
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None
    column_id: Optional[int] = None


# Properties to return to client (includes ID)
class TaskRead(TaskBase):
    id: int
