import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.rag import RagEvaluationRun
from app.infrastructure.database.models.rag import RagEvaluationRunModel

# SqlAlchemyNormativaChunkRepository vivio aqui hasta el cambio de arquitectura
# documentado en docs/saturdays_ai/00-plan.md §5: los chunks + embeddings de la
# normativa ahora se guardan y recuperan via LanceDbNormativaChunkRepository
# (ver app.infrastructure.database.lancedb_chunk_repository). Este archivo solo
# conserva SqlAlchemyRagEvaluationRunRepository, que sigue en Postgres sin
# cambios.


def _run_to_domain(model: RagEvaluationRunModel) -> RagEvaluationRun:
    return RagEvaluationRun(
        id=model.id,
        results=list(model.results),
        summary=dict(model.summary),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyRagEvaluationRunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, run: RagEvaluationRun) -> RagEvaluationRun:
        model = RagEvaluationRunModel(results=list(run.results), summary=dict(run.summary))
        self._session.add(model)
        self._session.flush()
        return _run_to_domain(model)

    def get_latest(self) -> RagEvaluationRun | None:
        model = self._session.scalar(
            select(RagEvaluationRunModel).order_by(RagEvaluationRunModel.created_at.desc()).limit(1)
        )
        return _run_to_domain(model) if model else None

    def get_by_id(self, run_id: uuid.UUID) -> RagEvaluationRun | None:
        model = self._session.get(RagEvaluationRunModel, run_id)
        return _run_to_domain(model) if model else None
