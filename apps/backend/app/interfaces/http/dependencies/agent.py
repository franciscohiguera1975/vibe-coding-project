from collections.abc import Callable

from fastapi import Depends

from app.application.ports.ai_provider import AIProvider
from app.application.ports.unit_of_work import UnitOfWork
from app.application.services.agent.ai_tutor_agent import AITutorAgent
from app.infrastructure.config import Settings, get_settings
from app.interfaces.http.dependencies.ai import get_ai_provider
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory


def get_ai_tutor_agent(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    ai_provider: AIProvider = Depends(get_ai_provider),
    settings: Settings = Depends(get_settings),
) -> AITutorAgent:
    return AITutorAgent(
        uow_factory,
        ai_provider,
        max_iterations=settings.ai_agent_max_iterations,
        max_tokens=settings.ai_agent_max_tokens,
    )
