from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.socket import manager

router = APIRouter()


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: int):
    await manager.connect(workspace_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from Workspace {workspace_id}: {data}")
            # 2. (The Echo Test) Broadcast it back to the room
            response_message = f"Workspace {workspace_id} update: {data}"
            await manager.broadcast(message=response_message, workspace_id=workspace_id)
    except WebSocketDisconnect:
        await manager.disconnect(workspace_id, websocket)
        await manager.broadcast("A user has left the chat.", workspace_id)
