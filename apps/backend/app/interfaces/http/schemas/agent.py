from typing import Any

from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    practice_slug: str
    user_message: str = ""
    submission_id: str | None = None
    trial_answer: dict[str, Any] | None = None
    image_base64: str | None = None
    image_content_type: str = "image/png"


class AgentRunResponse(BaseModel):
    session_id: str
    response: str
    iterations_used: int
    tokens_used: int
