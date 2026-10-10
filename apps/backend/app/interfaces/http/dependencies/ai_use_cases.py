from collections.abc import Callable

from fastapi import Depends

from app.application.ports.ai_provider import AIProvider
from app.application.ports.rag import EmbeddingPort
from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.ai.generate_hint import GenerateAIHintUseCase
from app.application.use_cases.ai.generate_practice_feedback import (
    GeneratePracticeFeedbackUseCase,
)
from app.interfaces.http.dependencies.ai import get_ai_provider
from app.interfaces.http.dependencies.rag import get_embedding_port
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory


def get_generate_hint_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    ai_provider: AIProvider = Depends(get_ai_provider),
    embedding_port: EmbeddingPort = Depends(get_embedding_port),
) -> GenerateAIHintUseCase:
    # embedding_port fundamenta la pista en normativa relacionada como demostracion
    # de que el motor de RAG es compartido (docs/saturdays_ai/00-plan.md §2); es
    # opcional y a prueba de fallos en GenerateAIHintUseCase, nunca bloquea la pista.
    return GenerateAIHintUseCase(uow_factory, ai_provider, embedding_port)


def get_generate_feedback_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    ai_provider: AIProvider = Depends(get_ai_provider),
) -> GeneratePracticeFeedbackUseCase:
    return GeneratePracticeFeedbackUseCase(uow_factory, ai_provider)
