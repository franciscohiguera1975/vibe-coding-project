import uuid

from fastapi import APIRouter, Depends

from app.application.use_cases.ai.generate_hint import GenerateAIHintUseCase
from app.application.use_cases.ai.generate_practice_feedback import (
    GeneratePracticeFeedbackUseCase,
)
from app.domain.entities.identity import User
from app.interfaces.http.dependencies.ai_use_cases import (
    get_generate_feedback_use_case,
    get_generate_hint_use_case,
)
from app.interfaces.http.dependencies.auth import get_current_user
from app.interfaces.http.schemas.ai import (
    FeedbackRequest,
    FeedbackResponse,
    HintRequest,
    HintResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/hint", response_model=HintResponse)
def generate_hint(
    payload: HintRequest,
    actor: User = Depends(get_current_user),
    use_case: GenerateAIHintUseCase = Depends(get_generate_hint_use_case),
) -> HintResponse:
    hint = use_case.execute(
        actor=actor, practice_slug=payload.practice_slug, student_context=payload.student_context
    )
    return HintResponse(hint=hint)


@router.post("/feedback", response_model=FeedbackResponse)
def generate_feedback(
    payload: FeedbackRequest,
    actor: User = Depends(get_current_user),
    use_case: GeneratePracticeFeedbackUseCase = Depends(get_generate_feedback_use_case),
) -> FeedbackResponse:
    feedback = use_case.execute(actor=actor, submission_id=uuid.UUID(payload.submission_id))
    return FeedbackResponse(feedback=feedback)
