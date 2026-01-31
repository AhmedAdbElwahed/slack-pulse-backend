from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class Column(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    order: int = Field(default=0)
    board_id: int = Field(foreign_key="board.id")

    # Relationship to Board (Parent)
    board: "Board" = Relationship(back_populates="columns")

    # Relationship to Task (Child)
    tasks: List["Task"] = Relationship(back_populates="column")
