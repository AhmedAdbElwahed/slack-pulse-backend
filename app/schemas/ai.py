from pydantic import BaseModel, Field
from typing import List


class SubTask(BaseModel):
    title: str = Field(..., description="A concise title for the task")
    description: str = Field(
        ..., description="A short description of what needs to be done"
    )
    estimated_hours: int = Field(..., description="Estimated time to complete in hours")


class ProjectBreakdown(BaseModel):
    tasks: List[SubTask]


class AIRequest(BaseModel):
    prompt: str
    column_id: int  # We need to know where to put these tasks
