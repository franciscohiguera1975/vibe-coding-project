from collections.abc import Callable
from datetime import UTC, datetime

from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.domain.entities.practice import PracticeStatus
from app.domain.entities.progress import ProgressStatus, StudentPracticeAttempt, StudentProgress
from app.domain.exceptions import NotFoundError, ValidationError


class StartPracticeUseCase:
    """StartPractice (Prompt Maestro §8, §19): crea un nuevo intento y registra/actualiza
    el progreso del estudiante. Solo se puede iniciar una practica publicada."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, practice_slug: str) -> StudentPracticeAttempt:
        with self._uow_factory() as uow:
            practice = uow.practices.get_by_slug(practice_slug)
            if practice is None or practice.status != PracticeStatus.PUBLISHED:
                raise NotFoundError("Practice", practice_slug)
            if practice.id is None:
                raise ValidationError("La practica no tiene id valido")

            now = datetime.now(UTC)
            attempt_number = (
                uow.practice_attempts.count_for_user_and_practice(actor.id, practice.id) + 1
            )
            attempt = uow.practice_attempts.add(
                StudentPracticeAttempt(
                    user_id=actor.id,
                    practice_id=practice.id,
                    attempt_number=attempt_number,
                    started_at=now,
                )
            )

            progress = uow.student_progress.get_by_user_and_practice(actor.id, practice.id)
            if progress is None:
                uow.student_progress.add(
                    StudentProgress(
                        user_id=actor.id,
                        practice_id=practice.id,
                        status=ProgressStatus.IN_PROGRESS,
                        attempts_count=1,
                        last_attempt_at=now,
                    )
                )
            else:
                progress.attempts_count += 1
                progress.last_attempt_at = now
                if progress.status == ProgressStatus.NOT_STARTED:
                    progress.status = ProgressStatus.IN_PROGRESS
                uow.student_progress.update(progress)

            uow.commit()
            return attempt
