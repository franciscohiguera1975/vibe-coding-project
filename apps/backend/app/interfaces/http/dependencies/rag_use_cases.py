from collections.abc import Callable

from fastapi import Depends

from app.application.ports.rag import EmbeddingPort, RagPort
from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.rag.run_evaluation import RunRagEvaluationUseCase
from app.application.use_cases.rag.validate_syllabus import ValidateSyllabusUseCase
from app.interfaces.http.dependencies.rag import get_embedding_port, get_rag_port
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory


def get_validate_syllabus_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    embedding_port: EmbeddingPort = Depends(get_embedding_port),
    rag_port: RagPort = Depends(get_rag_port),
) -> ValidateSyllabusUseCase:
    return ValidateSyllabusUseCase(uow_factory, embedding_port, rag_port)


def get_run_rag_evaluation_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    embedding_port: EmbeddingPort = Depends(get_embedding_port),
    rag_port: RagPort = Depends(get_rag_port),
) -> RunRagEvaluationUseCase:
    return RunRagEvaluationUseCase(uow_factory, embedding_port, rag_port)
