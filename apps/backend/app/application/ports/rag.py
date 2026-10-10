from typing import Protocol


class EmbeddingPort(Protocol):
    """Puerto de embeddings para el motor de RAG (docs/saturdays_ai/00-plan.md §5).
    Independiente de RagPort a proposito: los embeddings corren siempre localmente
    en el VPS (EMBEDDING_PROVIDER=local, sentence-transformers, sin red — ver
    LocalEmbeddingAdapter) para que la recuperacion nunca dependa de un tunel al
    HPC; solo la generacion (RagPort) se enruta hacia el HPC o un proveedor
    externo. Las implementaciones concretas viven en infrastructure/ai."""

    def embed(self, text: str) -> list[float]:
        """Calcula el embedding (vector denso) de `text`. Debe ser el mismo
        modelo/dimension para el corpus completo y para cada consulta en vivo —
        comparar vectores de espacios distintos no tiene sentido."""
        ...


class RagPort(Protocol):
    """Puerto de generacion del motor de RAG. Independiente de AIProvider (el del
    tutor existente) y de EmbeddingPort — su proveedor (RAG_LLM_PROVIDER) apunta
    por defecto a un LLM corrido en el HPC de CEDIA via un endpoint compatible con
    la API de OpenAI (vLLM + tunel SSH inverso, ver docs/saturdays_ai/02-hpc-pasos.md),
    intercambiable por cualquier otro endpoint compatible (p.ej. GitHub Models)
    cambiando solo RAG_BASE_URL. Las implementaciones concretas (MockRagAdapter,
    OpenAICompatibleRagAdapter) viven en infrastructure/ai."""

    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 1000) -> str:
        """Genera texto a partir de `prompt`, con un `system` prompt opcional."""
        ...
