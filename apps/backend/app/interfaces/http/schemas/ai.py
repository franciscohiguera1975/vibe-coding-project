from pydantic import BaseModel, Field


class HintRequest(BaseModel):
    practice_slug: str
    student_context: str = ""


class HintResponse(BaseModel):
    hint: str


class FeedbackRequest(BaseModel):
    submission_id: str = Field(min_length=1)


class FeedbackResponse(BaseModel):
    feedback: str
