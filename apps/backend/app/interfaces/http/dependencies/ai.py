from functools import lru_cache

from app.application.ports.ai_provider import AIProvider
from app.infrastructure.ai.mock_adapter import MockAIAdapter
from app.infrastructure.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    """Selecciona el adaptador segun AI_PROVIDER (Prompt Maestro §10). mock es el
    default en dev/test y no requiere credenciales."""
    settings = get_settings()
    if settings.ai_provider == "anthropic":
        from app.infrastructure.ai.anthropic_adapter import AnthropicAdapter

        if not settings.ai_api_key:
            raise RuntimeError("AI_PROVIDER=anthropic requiere AI_API_KEY configurada")
        return AnthropicAdapter(api_key=settings.ai_api_key, model=settings.ai_model)
    if settings.ai_provider == "openai_compatible":
        from app.infrastructure.ai.openai_compatible_ai_adapter import (
            OpenAICompatibleAiAdapter,
        )

        if not settings.ai_base_url:
            raise RuntimeError(
                "AI_PROVIDER=openai_compatible requiere AI_BASE_URL configurada"
            )
        return OpenAICompatibleAiAdapter(
            base_url=settings.ai_base_url,
            api_key=settings.ai_api_key,
            chat_model=settings.ai_model,
            vision_base_url=settings.ai_vision_base_url,
            vision_model=settings.ai_vision_model,
        )
    return MockAIAdapter()
