from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    hashed_password: str

    # Relationship to Workspace
    workspaces: List["Workspace"] = Relationship(back_populates="owner")
