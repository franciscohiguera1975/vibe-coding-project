from functools import lru_cache

from app.application.ports.narration import NarrationPort
from app.infrastructure.ai.mock_narration_adapter import MockNarrationAdapter
from app.infrastructure.config import get_settings


@lru_cache
def get_narration_port() -> NarrationPort:
    """Selecciona el adaptador segun NARRATION_PROVIDER (analogo a get_ai_provider).
    mock es el default en dev/test y no requiere credenciales."""
    settings = get_settings()
    if settings.narration_provider == "elevenlabs":
        from app.infrastructure.ai.elevenlabs_narration_adapter import (
            ElevenLabsNarrationAdapter,
        )

        if not settings.elevenlabs_api_key:
            raise RuntimeError(
                "NARRATION_PROVIDER=elevenlabs requiere ELEVENLABS_API_KEY configurada"
            )
        return ElevenLabsNarrationAdapter(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model_id,
        )
    return MockNarrationAdapter()
