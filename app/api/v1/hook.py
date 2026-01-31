from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db.session import get_session
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace
from app.models.board import Board
from app.models.column import Column

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.core.socket import manager
from app.schemas.events import EventType, SocketEvent


router = APIRouter(prefix="/hooks")


def get_workspace_id(session: Session, coulmn_id: int):
    """Traverse: Column -> Board -> Workspace ID"""
    coulmn = session.get(Column, coulmn_id)
    if not coulmn:
        return None
    board = session.get(Board, coulmn.board_id)
    if not board:
        return None
    return board.workspace_id


@router.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    # 1. DB Operation
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # 2. Resolve Workspace
    ws_id = get_workspace_id(session, db_task.column_id)

    # 3. WebSocket Hook
    if ws_id:
        event = SocketEvent(
            event_type=EventType.TASK_CREATED,
            data=db_task.model_dump(),
            workspace_id=ws_id,
        )
        await manager.broadcast(workspace_id=ws_id, message=event.model_dump())

    return db_task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)
):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if we are "Moving" (changing columns) or just "Updating" (text)
    is_move = (
        task_update.column_id is not None and task_update.column_id != db_task.column_id
    )
    event_type = EventType.TASK_MOVED if is_move else EventType.TASK_UPDATED

    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Hook
    ws_id = get_workspace_id(session, db_task.column_id)
    if ws_id:
        event = SocketEvent(
            event_type=event_type, data=db_task.model_dump(), workspace_id=ws_id
        )
        await manager.broadcast(workspace_id=ws_id, message=event.model_dump())

    return db_task


# --- READ (No Changes Needed) ---
@router.get("/tasks/", response_model=List[TaskRead])
def read_tasks(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# --- DELETE WITH HOOK ---
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Capture ID and WS_ID before deletion
    task_id_snapshot = task.id
    ws_id = get_workspace_id(session, task.column_id)

    session.delete(task)
    session.commit()

    # Hook
    if ws_id:
        event = SocketEvent(
            event_type=EventType.TASK_DELETED,
            data={"id": task_id_snapshot},  # Only need ID to remove from UI
            workspace_id=ws_id,
        )
        await manager.broadcast(workspace_id=ws_id, message=event.model_dump())
