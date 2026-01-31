from typing import Dict, List
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        # Store connections: {workspace_id: [socket1, socket2]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, workspace_id: int, websocket: WebSocket):
        """Accepts the connection and adds it to the workspace group."""
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)
        print(f"Client connected to Workspace {workspace_id}")

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
        """Sends a message to all users in a specific workspace."""
        if workspace_id in self.active_connections:
            json_message = json.dumps(message, default=str)
            for connection in self.active_connections[workspace_id]:
                try:
                    await connection.send_text(json_message)
                except Exception as e:
                    # If sending fails (e.g., socket closed), we might remove it here
                    # But usually, the 'disconnect' method handles cleanup.
                    print(f"Error broadcasting: {e}")


manager = ConnectionManager()
