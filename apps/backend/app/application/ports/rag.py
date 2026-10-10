from typing import Protocol


class EmbeddingPort(Protocol):
    """Puerto de embeddings para el motor de RAG (docs/saturdays_ai/00-plan.md §5).
    Independiente de RagPort a proposito: el proveedor real (TEI, vLLM, etc.)
    corre en el HPC de CEDIA, tunelado al VPS (ver docs/saturdays_ai/02-hpc-pasos.md);
    solo la BUSQUEDA sobre los vectores ya calculados (rag_retrieval.py, LanceDB)
    vive siempre en el VPS. Las implementaciones concretas viven en infrastructure/ai.

    `is_query` distingue consulta de pasaje porque algunos modelos (p.ej. la
    familia E5 — `intfloat/multilingual-e5-large`, el default de este proyecto)
    fueron entrenados con prefijos "query: "/"passage: " y dan resultados de
    recuperacion muy pobres (practicamente aleatorios) si se les da texto crudo
    sin ese prefijo — descubierto 2026-10-10 al ver que la recuperacion real
    colapsaba siempre en el mismo documento sin importar la pregunta."""

    def embed(self, text: str, *, is_query: bool = False) -> list[float]:
        """Calcula el embedding (vector denso) de `text`. `is_query=True` para
        el texto de una consulta en vivo (sílabo, pregunta de evaluación);
        `is_query=False` (default) para un fragmento del corpus que se indexa.
        Debe ser el mismo modelo/dimension para el corpus completo y para cada
        consulta — comparar vectores de espacios distintos no tiene sentido."""
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
