import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.domain.entities.progress import AttemptStatus, PracticeSubmission
from app.domain.exceptions import NotFoundError, PermissionDeniedError, ValidationError


class SubmitPracticeUseCase:
    """SubmitPractice (Prompt Maestro §8, §19)."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(
        self, *, actor: User, attempt_id: uuid.UUID, payload: dict[str, Any]
    ) -> PracticeSubmission:
        with self._uow_factory() as uow:
            attempt = uow.practice_attempts.get_by_id(attempt_id)
            if attempt is None:
                raise NotFoundError("StudentPracticeAttempt", str(attempt_id))
            if attempt.user_id != actor.id:
                raise PermissionDeniedError("practice:submit_own_attempt")
            if attempt.status != AttemptStatus.IN_PROGRESS:
                raise ValidationError("El intento ya fue enviado o finalizado")

            now = datetime.now(UTC)
            submission = uow.practice_submissions.add(
                PracticeSubmission(
                    attempt_id=attempt.id,
                    practice_id=attempt.practice_id,
                    user_id=actor.id,
                    payload=payload,
                    submitted_at=now,
                )
            )

            attempt.status = AttemptStatus.SUBMITTED
            attempt.finished_at = now
            uow.practice_attempts.update(attempt)

            uow.commit()
            return submission
