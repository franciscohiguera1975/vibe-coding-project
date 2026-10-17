import uuid
from typing import Protocol

from app.domain.entities.rag import NormativaChunk, RagEvaluationRun, RetrievedChunk


class NormativaChunkRepository(Protocol):
    def get_by_chunk_id(self, chunk_id: str) -> NormativaChunk | None: ...

    def upsert(self, chunk: NormativaChunk) -> NormativaChunk: ...

    def list_all(self) -> list[NormativaChunk]: ...

    def count(self) -> int: ...

    def search_hybrid(
        self, query_embedding: list[float], query_text: str, *, k: int = 3
    ) -> list[RetrievedChunk]:
        """Recuperacion hibrida (vectorial + palabra clave, fusionadas con RRF)
        resuelta por el motor de almacenamiento, no por quien llama — a
        diferencia de list_all(), que trae todo a Python."""
        ...


class RagEvaluationRunRepository(Protocol):
    def add(self, run: RagEvaluationRun) -> RagEvaluationRun: ...

    def get_latest(self) -> RagEvaluationRun | None: ...

    def get_by_id(self, run_id: uuid.UUID) -> RagEvaluationRun | None: ...
