from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio
import time
from app.db.redis_conn import redis_client


class ConnectionManager:
    def __init__(self):
        # Store connections: {workspace_id: [socket1, socket2]}
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.pubsub_client = None
        self.is_listening = False

    async def connect(self, workspace_id: int, websocket: WebSocket):
        """Accepts the connection and adds it to the workspace group."""
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
        print(f"Client connected to Workspace {workspace_id}")

        # Start the background Redis listener if it's not running
        if not self.is_listening:
            asyncio.create_task(self.start_redis_listener())

    async def disconnect(self, workspace_id: int, websocket: WebSocket):
        """Removes the connection when a user leaves."""
        if workspace_id in self.active_connections:
            if websocket in self.active_connections[workspace_id]:
                self.active_connections[workspace_id].remove(websocket)
                # Cleanup empty keys to save memory
                if not self.active_connections[workspace_id]:
                    del self.active_connections[workspace_id]
        print(f"Client disconnected from Workspace {workspace_id}")

    async def broadcast(self, workspace_id: int, message: dict):
        """
        1. Add timestamp/ID to message.
        2. Save to Redis History (Persistence).
        3. Publish to Redis (Scaling).
        """
        # Add metadata for reliability
        message["timestamp"] = time.time()
        message["event_id"] = f"{workspace_id}_{int(time.time()*1000)}"

        json_message = json.dumps(message)

        # A. Persistence: Store in Redis List (Cap at 50)
        history_key = f"pulse:history:{workspace_id}"
        async with redis_client.pipeline() as pipe:
            pipe.rpush(history_key, json_message)
            pipe.ltrim(history_key, -50, -1)
            pipe.publish("pulse:events", json_message)  # B. Scaling
            await pipe.execute()

    async def start_redis_listener(self):
        """Background task: Listens to Redis and forwards to local sockets"""
        self.is_listening = True
        self.pubsub_client = redis_client.pubsub()
        await self.pubsub_client.subscribe("pulse:events")

        async for message in self.pubsub_client.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                target_ws_id = int(data.get("workspace_id"))

                # Forward ONLY if we have local users for this workspace
                if target_ws_id in self.active_connections:
                    for connection in self.active_connections[target_ws_id]:
                        try:
                            await connection.send_text(message["data"])
                        except Exception as e:
                            pass


manager = ConnectionManager()
