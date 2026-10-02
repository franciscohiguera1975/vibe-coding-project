import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from app.application.ports.evaluation import EvaluationPort
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.progress import (
    AttemptStatus,
    EvaluatorType,
    PracticeEvaluation,
    ProgressStatus,
)
from app.domain.exceptions import NotFoundError, PermissionDeniedError


class EvaluatePracticeUseCase:
    """EvaluatePractice (Prompt Maestro §8, §19): evalua un envio con el EvaluationPort y
    actualiza el intento y el progreso del estudiante."""

    def __init__(
        self, uow_factory: Callable[[], UnitOfWork], evaluation_port: EvaluationPort
    ) -> None:
        self._uow_factory = uow_factory
        self._evaluation_port = evaluation_port

    def execute(self, *, actor: User, submission_id: uuid.UUID) -> PracticeEvaluation:
        with self._uow_factory() as uow:
            submission = uow.practice_submissions.get_by_id(submission_id)
            if submission is None:
                raise NotFoundError("PracticeSubmission", str(submission_id))

            is_owner = submission.user_id == actor.id
            if not is_owner and not actor.has_permission(perm.PRACTICE_READ):
                raise PermissionDeniedError(perm.PRACTICE_READ)

            practice = uow.practices.get_by_id(submission.practice_id)
            if practice is None:
                raise NotFoundError("Practice", str(submission.practice_id))

            result = self._evaluation_port.evaluate(
                practice=practice, submission_payload=submission.payload
            )
            evaluation = uow.practice_evaluations.add(
                PracticeEvaluation(
                    submission_id=submission.id,
                    score=result.score,
                    passed=result.passed,
                    evaluated_by=EvaluatorType.SYSTEM,
                    feedback=result.feedback,
                    details=result.details,
                )
            )

            attempt = uow.practice_attempts.get_by_id(submission.attempt_id)
            if attempt is not None:
                attempt.status = AttemptStatus.EVALUATED
                uow.practice_attempts.update(attempt)

            now = datetime.now(UTC)
            progress = uow.student_progress.get_by_user_and_practice(
                submission.user_id, submission.practice_id
            )
            if progress is not None:
                if progress.best_score is None or result.score > progress.best_score:
                    progress.best_score = result.score
                if result.passed and progress.status != ProgressStatus.COMPLETED:
                    progress.status = ProgressStatus.COMPLETED
                    progress.completed_at = now
                uow.student_progress.update(progress)

            uow.commit()
            return evaluation
