from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.task import Task
from app.schemas.ai import AIRequest
from app.core.ai_service import ai_service
from app.core.socket import manager
from app.schemas.events import EventType, SocketEvent
from app.api.v1.hook import get_workspace_id


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate-tasks/", status_code=201)
async def generate_tasks(request: AIRequest, session: Session = Depends(get_session)):
    """
    1. Accepts a high-level feature description.
    2. Uses Ollama to break it down.
    3. Saves tasks to DB.
    4. Broadcasts updates via WebSockets.
    """
    try:
        # 1. Get Breakdown from AI
        print(f"Asking AI to break down: {request.prompt}")
        breakdown = ai_service.breakdown_feature(request.prompt)

        created_tasks = []

        # 2. Save tasks to DB
        for subtask in breakdown.tasks:
            db_task = Task(
                title=subtask.title,
                description=f"{subtask.description} (Est: {subtask.estimated_hours}h)",
                status="todo",
                column_id=request.column_id,
                order=0,
            )
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            created_tasks.append(db_task.model_dump())

            # 3. Trigger WebSocket Hook (Reuse logic from Phase 3)
            ws_id = get_workspace_id(session, request.column_id)
            if ws_id:
                event = SocketEvent(
                    event_type=EventType.TASK_CREATED,
                    data=db_task.model_dump(),
                    workspace_id=ws_id,
                )
                await manager.broadcast(workspace_id=ws_id, message=event.model_dump())

        return {
            "status": "success",
            "tasks_created": len(created_tasks),
            "data": created_tasks,
        }

    except Exception as e:
        print(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
