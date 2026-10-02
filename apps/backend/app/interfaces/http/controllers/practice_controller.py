from app.domain.entities.practice import Practice
from app.domain.entities.progress import (
    PracticeEvaluation,
    PracticeSubmission,
    StudentPracticeAttempt,
)
from app.domain.value_objects.pagination import Page
from app.interfaces.http.schemas.practice import (
    AttemptResponse,
    EvaluationResponse,
    PracticeDetail,
    PracticeListResponse,
    PracticeSummary,
    SubmissionResponse,
)


def practice_to_summary(practice: Practice) -> PracticeSummary:
    return PracticeSummary(
        id=str(practice.id),
        slug=practice.slug,
        title=practice.title,
        description=practice.description,
        type=practice.type,
        difficulty=practice.difficulty.value,
        estimated_time_minutes=practice.estimated_time_minutes,
        technologies=practice.technologies,
        status=practice.status.value,
        category_id=str(practice.category_id) if practice.category_id else None,
    )


def practice_to_detail(practice: Practice) -> PracticeDetail:
    summary = practice_to_summary(practice)
    return PracticeDetail(
        **summary.model_dump(),
        objectives=practice.objectives,
        instructions=practice.instructions,
        content=practice.content,
        evaluation=practice.evaluation,
        ai_configuration=practice.ai_configuration,
        embedding_configuration=practice.embedding_configuration,
        metadata=practice.metadata,
    )


def page_to_response(page: Page[Practice]) -> PracticeListResponse:
    return PracticeListResponse(
        items=[practice_to_summary(p) for p in page.items],
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
