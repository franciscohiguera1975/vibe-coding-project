from functools import lru_cache

from app.application.ports.rag import EmbeddingPort, RagPort
from app.infrastructure.ai.mock_rag_adapter import MockRagAdapter
from app.infrastructure.config import get_settings

# Una unica instancia de MockRagAdapter cubre ambos puertos (EmbeddingPort y
# RagPort) en modo mock: es deterministica, sin red, igual patron que
# MockAIAdapter/MockNarrationAdapter (ver docs/saturdays_ai/00-plan.md §5).
_mock_rag_adapter = MockRagAdapter()


@lru_cache
def get_rag_port() -> RagPort:
    """Selecciona el adaptador de generacion segun RAG_LLM_PROVIDER (analogo a
    get_ai_provider/get_narration_port). mock es el default en dev/test y no
    requiere credenciales ni red."""
    settings = get_settings()
    if settings.rag_llm_provider == "openai_compatible":
        from app.infrastructure.ai.openai_compatible_rag_adapter import (
            OpenAICompatibleRagAdapter,
        )

        if not settings.rag_base_url:
            raise RuntimeError(
                "RAG_LLM_PROVIDER=openai_compatible requiere RAG_BASE_URL configurada"
            )
        return OpenAICompatibleRagAdapter(
            base_url=settings.rag_base_url,
            api_key=settings.rag_api_key,
            chat_model=settings.rag_chat_model,
        )
    return _mock_rag_adapter


@lru_cache
def get_embedding_port() -> EmbeddingPort:
    """Selecciona el adaptador de embeddings segun EMBEDDING_PROVIDER (analogo a
    get_rag_port). mock es el default en dev/test y no requiere credenciales ni
    red. Independiente de RAG_LLM_PROVIDER (ver docs/saturdays_ai/00-plan.md §5:
    embeddings y generacion son proveedores separados, aunque ambos puedan
    terminar apuntando al mismo HPC en produccion)."""
    settings = get_settings()
    if settings.embedding_provider == "tei":
        from app.infrastructure.ai.tei_embedding_adapter import TeiEmbeddingAdapter

        if not settings.embedding_base_url:
            raise RuntimeError("EMBEDDING_PROVIDER=tei requiere EMBEDDING_BASE_URL configurada")
        return TeiEmbeddingAdapter(base_url=settings.embedding_base_url)
    return _mock_rag_adapter
