from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="todo")
    order: int = Field(default=0)  # Good for reordering tasks later
    column_id: int = Field(foreign_key="column.id")

    # Relationship to Column (Parent)
    column: "Column" = Relationship(back_populates="tasks")
