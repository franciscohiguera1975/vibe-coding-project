import uuid

from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin

# NormativaChunkModel (tabla normativa_chunks) vivio aqui hasta el cambio de
# arquitectura documentado en docs/saturdays_ai/00-plan.md §5: los chunks +
# embeddings de la normativa se movieron a una tabla LanceDB embebida (ver
# app.infrastructure.database.lancedb_chunk_repository). rag_evaluation_runs
# (abajo) se queda en Postgres sin cambios — solo se movieron los embeddings.


class RagEvaluationRunModel(TimestampMixin, Base):
    """Resultado persistido de una corrida del set de evaluacion baseline-vs-RAG
    (rag_evaluation_runs, ver app.application.use_cases.rag.run_evaluation). Se
    guarda la corrida completa (no fila por pregunta) porque la pantalla
    "Evaluacion" siempre lee la mas reciente de una sola vez."""

    __tablename__ = "rag_evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    results: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    summary: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
