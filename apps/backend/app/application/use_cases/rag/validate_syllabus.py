from collections.abc import Callable
from dataclasses import dataclass

from app.application.ports.rag import EmbeddingPort, RagPort
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.domain.entities.rag import NormativaChunk
from app.domain.services.rag_retrieval import retrieve_top_k
from app.domain.services.syllabus_checklist import CHECKLIST_ITEMS, ChecklistItem, detect_item

_JUDGE_SYSTEM_PROMPT = (
    "Eres un asistente que verifica si un silabo universitario cumple con un "
    "requisito especifico de la normativa academica de la UTE. Se te entregan "
    "fragmentos reales de esa normativa como unico contexto valido: nunca "
    "inventes articulos ni cites normativa que no este en el contexto entregado. "
    "Inicie su respuesta con exactamente una de estas tres palabras en mayusculas "
    "seguida de dos puntos: 'CUMPLE:', 'NO_CUMPLE:' o 'NO_DETERMINADO:' (use "
    "NO_DETERMINADO solo si el contexto no alcanza para decidir), y luego, en "
    "2-4 frases en espanol, justifique citando explicitamente el articulo y el "
    "documento de origen."
)


@dataclass(frozen=True, slots=True)
class CitationRef:
    source_document: str
    article_label: str


@dataclass(frozen=True, slots=True)
class ChecklistItemResult:
    """Un resultado por item del checklist (ver syllabus_checklist.CHECKLIST_ITEMS).
    `cumple=None` significa que el LLM no pudo determinar cumplimiento (o que no
    se encontro normativa relevante, p.ej. si aun no se corrio load_chunks.py)."""

    item: str
    label: str
    cumple: bool | None
    explicacion: str
    citas: list[CitationRef]


class ValidateSyllabusUseCase:
    """ValidateSyllabus (docs/saturdays_ai/00-plan.md §6): caso de uso principal de
    la demo. Para cada item del checklist de contenido obligatorio de un silabo,
    recupera (RAG) los articulos de normativa mas relevantes y le pide al LLM
    configurado (RagPort) que juzgue si el silabo pegado cumple ese item,
    fundamentado y citando explicitamente la fuente."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        embedding_port: EmbeddingPort,
        rag_port: RagPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._embedding_port = embedding_port
        self._rag_port = rag_port

    def execute(self, *, actor: User, syllabus_text: str) -> list[ChecklistItemResult]:
        with self._uow_factory() as uow:
            all_chunks = uow.normativa_chunks.list_all()

        return [
            self._evaluate_item(item, syllabus_text, all_chunks) for item in CHECKLIST_ITEMS
        ]

    def _evaluate_item(
        self,
        item: ChecklistItem,
        syllabus_text: str,
        all_chunks: list[NormativaChunk],
    ) -> ChecklistItemResult:
        # La consulta de recuperacion combina la etiqueta del item y sus palabras
        # clave (no el silabo completo): buscamos el articulo que define ESE
        # requisito, no uno parecido al texto libre del estudiante.
        query = f"{item.label}: {' '.join(item.keywords)}"
        query_embedding = self._embedding_port.embed(query, is_query=True)
        retrieved = retrieve_top_k(query_embedding, all_chunks, k=3)

        if not retrieved:
            return ChecklistItemResult(
                item=item.key,
                label=item.label,
                cumple=None,
                explicacion=(
                    "No se encontraron articulos de normativa cargados para verificar "
                    "este item. Ejecute scripts/rag/load_chunks.py para cargar e "
                    "indexar el corpus."
                ),
                citas=[],
            )

        context_block = "\n\n".join(
            f"[{r.chunk.source_document} - {r.chunk.article_label}]\n{r.chunk.text}"
            for r in retrieved
        )
        heuristic_present = detect_item(item, syllabus_text)
        prompt = (
            f"Item del checklist a verificar: {item.label}\n\n"
            f"Fragmentos de la normativa relevante (unica fuente valida):\n{context_block}\n\n"
            f"Texto del silabo a evaluar:\n{syllabus_text or '(vacio)'}\n\n"
            "Determine si el silabo cumple con este item segun la normativa citada arriba."
        )
        answer = self._rag_port.generate(prompt, system=_JUDGE_SYSTEM_PROMPT, max_tokens=400)

        citas = [
            CitationRef(
                source_document=r.chunk.source_document, article_label=r.chunk.article_label
            )
            for r in retrieved
        ]
        return ChecklistItemResult(
            item=item.key,
            label=item.label,
            cumple=_infer_cumple(answer, heuristic_present),
            explicacion=answer,
            citas=citas,
        )


def _infer_cumple(answer: str, heuristic_present: bool) -> bool | None:
    normalized = answer.strip().upper()
    if normalized.startswith("NO_CUMPLE") or normalized.startswith("NO CUMPLE"):
        return False
    if normalized.startswith("NO_DETERMINADO") or normalized.startswith("NO DETERMINADO"):
        return None
    if normalized.startswith("CUMPLE"):
        return True
    # El LLM no siguio el formato pedido (ocurre siempre con MockRagAdapter en
    # pruebas/dev, y podria ocurrir con un LLM real que ignore la instruccion):
    # degradamos a la deteccion heuristica por palabra clave en vez de dejar un
    # veredicto vacio.
    return heuristic_present
