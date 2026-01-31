from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    workspace_id: int = Field(foreign_key="workspace.id")

    # Relationship to Workspace (Parent)
    workspace: "Workspace" = Relationship(back_populates="boards")

    # Relationship to Column (Child)
    columns: List["Column"] = Relationship(back_populates="board")
