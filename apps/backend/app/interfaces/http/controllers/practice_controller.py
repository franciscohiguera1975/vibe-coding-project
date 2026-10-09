from app.domain.entities.practice import Practice
from app.domain.entities.progress import (
    PracticeEvaluation,
    PracticeSubmission,
    StudentPracticeAttempt,
)
from app.domain.services.practice_localization import localize_practice
from app.domain.value_objects.pagination import Page
from app.interfaces.http.schemas.practice import (
    AttemptResponse,
    EvaluationResponse,
    PracticeAdminDetail,
    PracticeDetail,
    PracticeListResponse,
    PracticeSummary,
    SubmissionResponse,
)


def practice_to_summary(practice: Practice, lang: str | None = None) -> PracticeSummary:
    localized = localize_practice(practice, lang)
    return PracticeSummary(
        id=str(practice.id),
        slug=practice.slug,
        title=localized.title,
        description=localized.description,
        type=practice.type,
        difficulty=practice.difficulty.value,
        estimated_time_minutes=practice.estimated_time_minutes,
        technologies=practice.technologies,
        status=practice.status.value,
        category_id=str(practice.category_id) if practice.category_id else None,
    )


def practice_to_detail(practice: Practice, lang: str | None = None) -> PracticeDetail:
    summary = practice_to_summary(practice, lang)
    localized = localize_practice(practice, lang)
    return PracticeDetail(
        **summary.model_dump(),
        objectives=localized.objectives,
        instructions=localized.instructions,
        content=localized.content,
        evaluation=practice.evaluation,
        ai_configuration=practice.ai_configuration,
        embedding_configuration=practice.embedding_configuration,
        metadata=practice.metadata,
    )


def practice_to_admin_detail(practice: Practice) -> PracticeAdminDetail:
    """Respuesta para los endpoints de administracion (crear/actualizar/publicar):
    igual que `practice_to_detail` en espanol (la base editable) mas el diccionario
    crudo `translations`, nunca expuesto en los endpoints publicos."""
    detail = practice_to_detail(practice, lang=None)
    return PracticeAdminDetail(**detail.model_dump(), translations=practice.translations)


def page_to_response(page: Page[Practice], lang: str | None = None) -> PracticeListResponse:
    return PracticeListResponse(
        items=[practice_to_summary(p, lang) for p in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )


def attempt_to_response(attempt: StudentPracticeAttempt) -> AttemptResponse:
    return AttemptResponse(
        id=str(attempt.id),
        practice_id=str(attempt.practice_id),
        attempt_number=attempt.attempt_number,
        status=attempt.status.value,
        started_at=attempt.started_at,
        finished_at=attempt.finished_at,
    )


def submission_to_response(submission: PracticeSubmission) -> SubmissionResponse:
    return SubmissionResponse(
        id=str(submission.id),
        attempt_id=str(submission.attempt_id),
        submitted_at=submission.submitted_at,
    )


def evaluation_to_response(evaluation: PracticeEvaluation) -> EvaluationResponse:
    return EvaluationResponse(
        id=str(evaluation.id),
        submission_id=str(evaluation.submission_id),
        score=evaluation.score,
        passed=evaluation.passed,
        feedback=evaluation.feedback,
        details=evaluation.details,
    )
