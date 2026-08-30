from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.economy.models import RewardLedger
from app.modules.grading.evaluator import evaluator
from app.modules.grading.models import Attempt
from app.modules.identity.models import User
from app.modules.learning.models import LearningTask


def grade_attempt(attempt_id: int) -> None:
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

        result = evaluator.evaluate(attempt.code, task.reference_solution)
        attempt.is_correct = result.is_correct
        attempt.result_message = result.message
        attempt.status = "COMPLETED"
        attempt.completed_at = datetime.now(timezone.utc)

        if result.is_correct:
            already_rewarded = db.scalar(
                select(RewardLedger.id).where(RewardLedger.attempt_id == attempt.id)
            )
            if already_rewarded is None:
                user = db.get(User, attempt.user_id)
                if user is not None:
                    user.balance += task.reward_amount
                    db.add(
                        RewardLedger(
                            attempt_id=attempt.id,
                            user_id=attempt.user_id,
                            amount=task.reward_amount,
                        )
                    )
        db.commit()
