import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class NormativaChunk:
    """Un fragmento (articulo o parrafo) de la normativa institucional de la UTE,
    con su embedding ya calculado (ver scripts/rag/ingest_normativa.py para la
    extraccion y scripts/rag/load_chunks.py para el calculo del embedding e
    insercion). `chunk_id` es la clave natural que viene de chunks.jsonl —
    estable entre corridas del script de ingestion."""

    chunk_id: str
    source_document: str
    article_label: str
    text: str
    embedding: list[float] = field(default_factory=list)
    id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """Un NormativaChunk recuperado para una consulta concreta, con su score de
    similitud (coseno, ver app.domain.services.rag_retrieval)."""

    chunk: NormativaChunk
    score: float


@dataclass(slots=True)
class RagEvaluationRun:
    """Una corrida completa del set de evaluacion (baseline vs RAG, ver
    app.application.use_cases.rag.run_evaluation). `results` es la lista de
    {id, question, baseline_answer, rag_answer, expected_citation,
    rag_citation_match, baseline_citation_match}; `summary` trae los conteos
    agregados que muestra la pantalla "Evaluacion"."""

    results: list[dict[str, Any]]
    summary: dict[str, Any]
    id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
