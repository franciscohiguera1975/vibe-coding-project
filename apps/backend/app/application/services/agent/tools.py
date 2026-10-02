"""Herramientas controladas del AI Tutor Agent (Prompt Maestro §11). Cada funcion
recibe (uow, actor, ai_provider, **kwargs) y devuelve un dict serializable — nunca
muta practicas, usuarios ni configuraciones: son de solo lectura o de generacion,
nunca administrativas ni destructivas."""

import base64
import uuid
from typing import Any, Protocol

from app.application.ports.ai_provider import AIProvider
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.domain.exceptions import NotFoundError, PermissionDeniedError
from app.infrastructure.evaluation.rule_based_adapter import RuleBasedEvaluationAdapter

_HINT_SYSTEM_PROMPT = (
    "Eres un tutor de un curso de Vibe Coding. Da una pista breve que oriente al "
    "estudiante hacia la solucion sin revelarla por completo ni inventar informacion "
    "que no este en las instrucciones de la practica."
)


class AgentTool(Protocol):
    def __call__(
        self, uow: UnitOfWork, actor: User, ai_provider: AIProvider, **kwargs: Any
    ) -> dict[str, Any]: ...


def tool_get_practice(
    uow: UnitOfWork, actor: User, ai_provider: AIProvider, *, practice_slug: str
) -> dict[str, Any]:
    practice = uow.practices.get_by_slug(practice_slug)
    if practice is None:
        raise NotFoundError("Practice", practice_slug)
    return {
        "id": str(practice.id),
        "title": practice.title,
        "type": practice.type,
        "instructions": practice.instructions,
        "objectives": practice.objectives,
        "difficulty": practice.difficulty.value,
    }


def tool_get_student_progress(
    uow: UnitOfWork, actor: User, ai_provider: AIProvider, *, practice_slug: str
) -> dict[str, Any]:
    practice = uow.practices.get_by_slug(practice_slug)
    if practice is None:
        raise NotFoundError("Practice", practice_slug)
    progress = uow.student_progress.get_by_user_and_practice(actor.id, practice.id)
    if progress is None:
        return {"status": "not_started", "attempts_count": 0, "best_score": None}
    return {
        "status": progress.status.value,
        "attempts_count": progress.attempts_count,
        "best_score": progress.best_score,
    }


def tool_analyze_submission(
    uow: UnitOfWork, actor: User, ai_provider: AIProvider, *, submission_id: str
) -> dict[str, Any]:
    submission = uow.practice_submissions.get_by_id(uuid.UUID(submission_id))
    if submission is None:
        raise NotFoundError("PracticeSubmission", submission_id)
    if submission.user_id != actor.id:
        raise PermissionDeniedError("practice:read_own_submission")
    evaluation = uow.practice_evaluations.get_by_submission_id(submission.id)
    return {
        "payload": submission.payload,
        "evaluation": (
            {"score": evaluation.score, "passed": evaluation.passed, "details": evaluation.details}
            if evaluation
            else None
        ),
    }


def tool_generate_hint(
    uow: UnitOfWork,
    actor: User,
    ai_provider: AIProvider,
    *,
    practice_slug: str,
    student_context: str = "",
) -> dict[str, Any]:
    practice = uow.practices.get_by_slug(practice_slug)
    if practice is None:
        raise NotFoundError("Practice", practice_slug)
    prompt = (
        f"Practica: {practice.title}\nInstrucciones: {practice.instructions}\n"
        f"Contenido: {practice.content}\n"
        f"Lo que el estudiante ha intentado hasta ahora: {student_context or 'nada aun'}\n"
        "Genere una pista."
    )
    hint = ai_provider.generate_text(prompt, system=_HINT_SYSTEM_PROMPT, max_tokens=300)
    return {"hint": hint}


def tool_validate_answer(
    uow: UnitOfWork,
    actor: User,
    ai_provider: AIProvider,
    *,
    practice_slug: str,
    trial_answer: dict[str, Any],
) -> dict[str, Any]:
    """Verificacion de prueba (no oficial): no crea un intento ni un envio; solo
    aplica la misma regla de EvaluatePractice para orientar al estudiante."""
    practice = uow.practices.get_by_slug(practice_slug)
    if practice is None:
        raise NotFoundError("Practice", practice_slug)
    result = RuleBasedEvaluationAdapter().evaluate(
        practice=practice, submission_payload=trial_answer
    )
    return {"would_pass": result.passed, "would_score": result.score, "details": result.details}


def tool_analyze_image(
    uow: UnitOfWork,
    actor: User,
    ai_provider: AIProvider,
    *,
    image_base64: str,
    instructions: str,
    content_type: str = "image/png",
) -> dict[str, Any]:
    image_bytes = base64.b64decode(image_base64)
    result = ai_provider.analyze_image(
        image_bytes, instructions=instructions, content_type=content_type
    )
    return {"count": result.count, "warnings": result.warnings, "details": result.details}


def tool_generate_feedback(
    uow: UnitOfWork, actor: User, ai_provider: AIProvider, *, submission_id: str
) -> dict[str, Any]:
    submission = uow.practice_submissions.get_by_id(uuid.UUID(submission_id))
    if submission is None:
        raise NotFoundError("PracticeSubmission", submission_id)
    if submission.user_id != actor.id:
        raise PermissionDeniedError("practice:read_own_submission")
    practice = uow.practices.get_by_id(submission.practice_id)
    if practice is None:
        raise NotFoundError("Practice", str(submission.practice_id))
    evaluation = uow.practice_evaluations.get_by_submission_id(submission.id)
    context = {
        "practice_title": practice.title,
        "submission_payload": submission.payload,
        "score": evaluation.score if evaluation else None,
        "passed": evaluation.passed if evaluation else None,
    }
    feedback = ai_provider.generate_feedback(context=context)
    return {"feedback": feedback}


TOOL_REGISTRY: dict[str, AgentTool] = {
    "get_practice": tool_get_practice,
    "get_student_progress": tool_get_student_progress,
    "analyze_submission": tool_analyze_submission,
    "generate_hint": tool_generate_hint,
    "validate_answer": tool_validate_answer,
    "analyze_image": tool_analyze_image,
    "generate_feedback": tool_generate_feedback,
}
