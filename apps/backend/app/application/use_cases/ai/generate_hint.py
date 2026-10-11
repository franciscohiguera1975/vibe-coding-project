import logging
from collections.abc import Callable

from app.application.ports.ai_provider import AIProvider
from app.application.ports.rag import EmbeddingPort
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.domain.entities.practice import Practice
from app.domain.exceptions import NotFoundError
from app.domain.services.rag_retrieval import retrieve_top_k

logger = logging.getLogger(__name__)

_HINT_SYSTEM_PROMPT = (
    "Eres un tutor de un curso de Vibe Coding. Da una pista breve que oriente al "
    "estudiante hacia la solucion sin revelarla por completo ni inventar informacion "
    "que no este en las instrucciones de la practica."
)


class GenerateAIHintUseCase:
    """GenerateAIHint (Prompt Maestro §8, §11): una pista por practica, nunca la
    respuesta exacta. Cualquier usuario autenticado puede pedir una pista.

    `embedding_port` es OPCIONAL (docs/saturdays_ai/00-plan.md §2: el AI Tutor se
    complementa con el mismo motor de RAG del proyecto Saturdays AI, como
    demostracion de que es generico/reusable, no una pantalla nueva). Si no se
    pasa (valor por defecto, y el unico usado por el resto de la plataforma hasta
    ahora), el comportamiento es identico al de antes de este cambio. Si se pasa,
    se intenta fundamentar la pista con normativa institucional relacionada; si
    esa recuperacion falla por cualquier motivo (proveedor no disponible, tabla
    aun vacia, etc.) se ignora en silencio y la pista se genera exactamente como
    antes — nunca debe haber riesgo de regresion por este paso adicional."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        ai_provider: AIProvider,
        embedding_port: EmbeddingPort | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._ai_provider = ai_provider
        self._embedding_port = embedding_port

    def execute(self, *, actor: User, practice_slug: str, student_context: str = "") -> str:
        with self._uow_factory() as uow:
            practice = uow.practices.get_by_slug(practice_slug)
            grounding = self._retrieve_grounding(uow, practice) if practice is not None else ""

        if practice is None:
            raise NotFoundError("Practice", practice_slug)

        prompt = (
            f"Practica: {practice.title}\n"
            f"Instrucciones: {practice.instructions}\n"
            f"Contenido: {practice.content}\n"
            f"{grounding}"
            f"Lo que el estudiante ha intentado hasta ahora: {student_context or 'nada aun'}\n"
            "Genere una pista."
        )
        return self._ai_provider.generate_text(prompt, system=_HINT_SYSTEM_PROMPT, max_tokens=300)

    def _retrieve_grounding(self, uow: UnitOfWork, practice: Practice) -> str:
        """Recuperacion OPCIONAL y aditiva de normativa relacionada (mismo motor que
        ValidateSyllabusUseCase: EmbeddingPort + rag_retrieval.retrieve_top_k).
        Envuelto en try/except a proposito: ver docstring de la clase."""
        if self._embedding_port is None:
            return ""
        try:
            chunks = uow.normativa_chunks.list_all()
            if not chunks:
                return ""
            query = f"{practice.title} {practice.instructions}".strip()
            if not query:
                return ""
            query_embedding = self._embedding_port.embed(query)
            retrieved = retrieve_top_k(query_embedding, query, chunks, k=2)
            if not retrieved:
                return ""
            citations = "; ".join(
                f"{r.chunk.source_document} ({r.chunk.article_label})" for r in retrieved
            )
            return (
                "Normativa institucional relacionada (solo contexto adicional, no es "
                f"el foco de la pista): {citations}\n"
            )
        except Exception:  # noqa: BLE001 - el grounding es opcional, nunca debe romper la pista
            logger.warning(
                "No se pudo recuperar normativa para fundamentar la pista (se continua "
                "sin ese contexto adicional)",
                exc_info=True,
            )
            return ""
