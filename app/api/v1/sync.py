from fastapi import APIRouter
from typing import List
import json
from app.db.redis_conn import redis_client

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/workspaces/{workspace_id}/sync")
async def sync_events(workspace_id: int):
    """
    Returns the last 50 events for this workspace.
    The frontend can filter these using its own 'last_known_event_id'.
    """
    history_key = f"pulse:history:{workspace_id}"

    # Fetch all items in the list
    raw_events = await redis_client.lrange(history_key, 0, -1)

    # Parse JSON
    events = [json.loads(e) for e in raw_events]

    return {"events": events}
