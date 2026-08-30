from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.grading.models import Attempt
from app.modules.grading.service import grade_attempt_bounded
from app.modules.identity.models import User
from app.modules.learning.models import LearningTask

router = APIRouter(tags=["grading"])


class SubmissionRequest(BaseModel):
    user_id: int
    code: str


@router.post("/tasks/{task_id}/submissions", status_code=status.HTTP_202_ACCEPTED)
def submit_code(
    task_id: int,
    payload: SubmissionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    if db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=404, detail="user not found")
    if db.get(LearningTask, task_id) is None:
        raise HTTPException(status_code=404, detail="task not found")

    attempt = Attempt(user_id=payload.user_id, task_id=task_id, code=payload.code, status="PENDING")
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    background_tasks.add_task(grade_attempt_bounded, attempt.id)
    return {"attempt_id": attempt.id, "status": attempt.status}


@router.get("/attempts/{attempt_id}")
def get_attempt(attempt_id: int, db: Session = Depends(get_db)) -> dict:
    attempt = db.get(Attempt, attempt_id)
    if attempt is None:
        raise HTTPException(status_code=404, detail="attempt not found")
    return {
        "id": attempt.id,
        "user_id": attempt.user_id,
        "task_id": attempt.task_id,
        "status": attempt.status,
        "is_correct": attempt.is_correct,
        "result_message": attempt.result_message,
    }
