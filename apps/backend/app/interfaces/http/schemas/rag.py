from pydantic import BaseModel


class ValidateSyllabusRequest(BaseModel):
    text: str


class CitationRefResponse(BaseModel):
    source_document: str
    article_label: str


class ChecklistItemResultResponse(BaseModel):
    item: str
    label: str
    cumple: bool | None
    explicacion: str
    citas: list[CitationRefResponse]


class RagEvaluationResultItem(BaseModel):
    id: str
    question: str
    expected_citation: CitationRefResponse
    baseline_answer: str
    rag_answer: str
    rag_citation_match: bool
    baseline_citation_match: bool


class RagEvaluationRunResponse(BaseModel):
    id: str
    results: list[RagEvaluationResultItem]
    summary: dict[str, int]
