import uuid
from collections.abc import Callable

from app.application.ports.ai_provider import AIProvider
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.exceptions import NotFoundError, PermissionDeniedError


class GeneratePracticeFeedbackUseCase:
    """GeneratePracticeFeedback (Prompt Maestro §8): retroalimentacion personalizada
    generada por IA, complementaria a la evaluacion basada en reglas (EvaluatePractice)."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], ai_provider: AIProvider) -> None:
        self._uow_factory = uow_factory
        self._ai_provider = ai_provider

    def execute(self, *, actor: User, submission_id: uuid.UUID) -> str:
        with self._uow_factory() as uow:
            submission = uow.practice_submissions.get_by_id(submission_id)
            if submission is None:
                raise NotFoundError("PracticeSubmission", str(submission_id))

            if submission.user_id != actor.id and not actor.has_permission(perm.PRACTICE_READ):
                raise PermissionDeniedError(perm.PRACTICE_READ)

            practice = uow.practices.get_by_id(submission.practice_id)
            if practice is None:
                raise NotFoundError("Practice", str(submission.practice_id))

            evaluation = uow.practice_evaluations.get_by_submission_id(submission_id)

        context = {
            "practice_title": practice.title,
            "instructions": practice.instructions,
            "submission_payload": submission.payload,
            "score": evaluation.score if evaluation else None,
            "passed": evaluation.passed if evaluation else None,
            "details": evaluation.details if evaluation else None,
        }
        return self._ai_provider.generate_feedback(context=context)
