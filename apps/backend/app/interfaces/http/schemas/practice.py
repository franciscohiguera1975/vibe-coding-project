from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PracticeSummary(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    type: str
    difficulty: str
    estimated_time_minutes: int
    technologies: list[str]
    status: str
    category_id: str | None


class PracticeDetail(PracticeSummary):
    objectives: list[str]
    instructions: str
    content: dict[str, Any]
    evaluation: dict[str, Any]
    ai_configuration: dict[str, Any]
    embedding_configuration: dict[str, Any]
    metadata: dict[str, Any]


class PracticeAdminDetail(PracticeDetail):
    """Variante de PracticeDetail para el panel de administracion: ademas de los
    campos publicos (ya localizados segun `lang`) expone el diccionario crudo de
    `translations` para que un futuro editor de traducciones pueda leerlo/escribirlo.
    Nunca se usa en los endpoints publicos de catalogo/detalle."""

    translations: dict[str, Any] = Field(default_factory=dict)


class PracticeListResponse(BaseModel):
    items: list[PracticeSummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class CreatePracticeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    type: str
    slug: str | None = None
    description: str = ""
    objectives: list[str] = Field(default_factory=list)
    instructions: str = ""
    category_slug: str | None = None
    difficulty: str = "beginner"
    estimated_time_minutes: int = Field(default=30, ge=1)
    technologies: list[str] = Field(default_factory=list)
    tag_names: list[str] = Field(default_factory=list)
    content: dict[str, Any] = Field(default_factory=dict)
    evaluation: dict[str, Any] = Field(default_factory=dict)
    ai_configuration: dict[str, Any] = Field(default_factory=dict)
    embedding_configuration: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    translations: dict[str, Any] = Field(default_factory=dict)


class UpdatePracticeRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    objectives: list[str] | None = None
    instructions: str | None = None
    category_slug: str | None = None
    difficulty: str | None = None
    estimated_time_minutes: int | None = Field(default=None, ge=1)
    technologies: list[str] | None = None
    tag_names: list[str] | None = None
    content: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    ai_configuration: dict[str, Any] | None = None
    embedding_configuration: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    translations: dict[str, Any] | None = None


class AttemptResponse(BaseModel):
    id: str
    practice_id: str
    attempt_number: int
    status: str
    started_at: datetime
    finished_at: datetime | None


class SubmitPracticeRequest(BaseModel):
    attempt_id: str
    payload: dict[str, Any]


class SubmissionResponse(BaseModel):
    id: str
    attempt_id: str
    submitted_at: datetime


class EvaluationResponse(BaseModel):
    id: str
    submission_id: str
    score: float
    passed: bool
    feedback: str
    details: dict[str, Any]


class NarrationResponse(BaseModel):
    lang: str
    url: str
    cached: bool


class NarrationPublicResponse(BaseModel):
    url: str


class NarrationGenerateAllItem(BaseModel):
    lang: str
    status: str
    url: str | None = None
    cached: bool | None = None
    message: str | None = None
