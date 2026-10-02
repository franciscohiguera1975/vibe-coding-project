from fastapi import APIRouter, Depends

from app.application.services.agent.ai_tutor_agent import AITutorAgent
from app.domain.entities.identity import User
from app.interfaces.http.dependencies.agent import get_ai_tutor_agent
from app.interfaces.http.dependencies.auth import get_current_user
from app.interfaces.http.schemas.agent import AgentRunRequest, AgentRunResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=AgentRunResponse)
def run_agent(
    payload: AgentRunRequest,
    actor: User = Depends(get_current_user),
    agent: AITutorAgent = Depends(get_ai_tutor_agent),
) -> AgentRunResponse:
    result = agent.run(
        actor=actor,
        practice_slug=payload.practice_slug,
        user_message=payload.user_message,
        submission_id=payload.submission_id,
        trial_answer=payload.trial_answer,
        image_base64=payload.image_base64,
        image_content_type=payload.image_content_type,
    )
    return AgentRunResponse(
        session_id=str(result.session_id),
        response=result.response,
        iterations_used=result.iterations_used,
        tokens_used=result.tokens_used,
    )
