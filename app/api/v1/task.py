from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db.session import get_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter()


# --- CREATE ---
@router.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    # 1. Convert Schema -> DB Model
    db_task = Task.model_validate(task)

    # 2. Add and Commit
    session.add(db_task)
    session.commit()

    # 3. Refresh to get the generated ID
    session.refresh(db_task)
    return db_task


# --- READ ALL ---
@router.get("/tasks/", response_model=List[TaskRead])
def read_tasks(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks


# --- READ ONE ---
@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# --- UPDATE ---
@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session)
):
    # 1. Get existing task
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Update only provided fields
    task_data = task_update.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


# --- DELETE ---
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    # 204 No Content returns nothing
