from pydantic import BaseModel
from typing import Any, Optional


class EventType:
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_MOVED = "TASK_MOVED"
    TASK_DELETED = "TASK_DELETED"


class SocketEvent(BaseModel):
    event_type: str
    data: Any
    workspace_id: int
