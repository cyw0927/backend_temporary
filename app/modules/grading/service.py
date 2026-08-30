from datetime import datetime, timezone
from threading import BoundedSemaphore

from sqlalchemy import select, update

from app.db.session import SessionLocal
from app.modules.economy.models import RewardLedger
from app.modules.grading.evaluator import evaluator
from app.modules.grading.models import Attempt
from app.modules.identity.models import User
from app.modules.learning.models import LearningTask


_grading_slots = BoundedSemaphore(value=4)


def grade_attempt_bounded(attempt_id: int) -> None:
    """Bound concurrent in-process grading work until a durable queue replaces it."""
    with _grading_slots:
        grade_attempt(attempt_id)


def grade_attempt(attempt_id: int) -> None:
    # Phase 1: read the immutable evaluation inputs, then close the DB session.
    # A future Docker/external evaluator must never run while a DB lock is held.
    with SessionLocal() as db:
        attempt = db.get(Attempt, attempt_id)
        if attempt is None or attempt.status != "PENDING":
            return
        task = db.get(LearningTask, attempt.task_id)
        if task is None:
            submitted_code = None
            reference_solution = None
        else:
            submitted_code = attempt.code
            reference_solution = task.reference_solution

    if submitted_code is None or reference_solution is None:
        with SessionLocal() as db:
            attempt = db.scalar(select(Attempt).where(Attempt.id == attempt_id).with_for_update())
            if attempt is not None and attempt.status == "PENDING":
                attempt.status = "FAILED"
                attempt.result_message = "task not found"
                attempt.completed_at = datetime.now(timezone.utc)
                db.commit()
        return

    result = evaluator.evaluate(submitted_code, reference_solution)

    # Phase 2: reacquire the attempt row and atomically persist result + one-time reward.
    with SessionLocal() as db:
        attempt = db.scalar(select(Attempt).where(Attempt.id == attempt_id).with_for_update())
        if attempt is None or attempt.status != "PENDING":
            return
        task = db.get(LearningTask, attempt.task_id)
        if task is None:
            attempt.status = "FAILED"
            attempt.result_message = "task not found"
            attempt.completed_at = datetime.now(timezone.utc)
            db.commit()
            return

        attempt.is_correct = result.is_correct
        attempt.result_message = result.message
        attempt.status = "COMPLETED"
        attempt.completed_at = datetime.now(timezone.utc)

        if result.is_correct:
            already_rewarded = db.scalar(
                select(RewardLedger.id).where(RewardLedger.attempt_id == attempt.id)
            )
            if already_rewarded is None:
                rewarded_user_id = db.scalar(
                    update(User)
                    .where(User.id == attempt.user_id)
                    .values(balance=User.balance + task.reward_amount)
                    .returning(User.id)
                )
                if rewarded_user_id is not None:
                    db.add(
                        RewardLedger(
                            attempt_id=attempt.id,
                            user_id=attempt.user_id,
                            amount=task.reward_amount,
                        )
                    )
        db.commit()
