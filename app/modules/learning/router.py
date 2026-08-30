from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.learning.models import LearningTask

router = APIRouter(prefix="/tasks", tags=["learning"])


def _task_payload(task: LearningTask) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "starter_code": task.starter_code,
        "reward_amount": task.reward_amount,
    }


@router.get("")
def list_tasks(db: Session = Depends(get_db)) -> list[dict]:
    return [_task_payload(task) for task in db.scalars(select(LearningTask).order_by(LearningTask.id)).all()]


@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)) -> dict:
    task = db.get(LearningTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return _task_payload(task)
