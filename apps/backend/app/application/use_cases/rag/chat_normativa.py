from collections.abc import Callable
from dataclasses import dataclass

from app.application.ports.rag import EmbeddingPort, RagPort
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User

_SYSTEM_PROMPT = (
    "Eres un asistente que responde preguntas sobre normativa academica y de "
    "educacion superior de la UTE. Se te entregan fragmentos reales de esa "
    "normativa como contexto, recuperados por busqueda semantica y por palabra "
    "clave. Si los fragmentos son relevantes para la pregunta, basa tu respuesta "
    "en ellos y cite siempre el articulo y el documento exacto. Si los "
    "fragmentos NO son relevantes o no contienen informacion suficiente, dilo "
    "explicitamente al inicio de tu respuesta (por ejemplo: 'Los fragmentos "
    "consultados no cubren este tema; respondo con conocimiento general, no "
    "verificado contra la normativa indexada:') y luego responde con tu "
    "conocimiento general sobre educacion superior. Nunca presentes "
    "conocimiento general como si fuera una cita de la normativa de la UTE."
)


@dataclass(frozen=True, slots=True)
class ChatCitation:
    source_document: str
    article_label: str


@dataclass(frozen=True, slots=True)
class ChatAnswer:
    """Respuesta del chat de normativa. `citations` son los fragmentos
    consultados (recuperados), no necesariamente los que el modelo termino
    usando — se muestran siempre para transparencia (igual criterio que la
    guia 24: mostrar el fragmento recuperado antes de confiar en la
    respuesta), independientemente de si el modelo los considero relevantes."""

    answer: str
    citations: list[ChatCitation]


class ChatNormativaUseCase:
    """ChatNormativa: pregunta libre sobre normativa academica, respondida con
    el mismo motor de recuperacion hibrida (BM25 + vectorial + RRF) que
    ValidateSyllabusUseCase, pero sin checklist fijo — una sola pregunta, una
    sola respuesta, sin memoria de conversacion entre llamadas. A diferencia
    de ValidateSyllabusUseCase, si la normativa indexada no cubre la pregunta
    el LLM puede responder con conocimiento general, marcandolo explicitamente
    (ver _SYSTEM_PROMPT) — ValidateSyllabusUseCase nunca hace esto a proposito
    (ahi un `NO_DETERMINADO` es el comportamiento correcto), pero un chat de
    consultas generales no seria muy util si solo pudiera hablar de los 896
    fragmentos indexados."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        embedding_port: EmbeddingPort,
        rag_port: RagPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._embedding_port = embedding_port
        self._rag_port = rag_port

    def execute(self, *, actor: User, question: str) -> ChatAnswer:
        query_embedding = self._embedding_port.embed(question, is_query=True)
        with self._uow_factory() as uow:
            retrieved = uow.normativa_chunks.search_hybrid(query_embedding, question, k=3)

        citations = [
            ChatCitation(
                source_document=r.chunk.source_document, article_label=r.chunk.article_label
            )
            for r in retrieved
        ]

        if not retrieved:
            prompt = (
                f"Pregunta: {question}\n\n"
                "No hay fragmentos de normativa cargados todavia. Indica que no "
                "puedes verificar contra la normativa de la UTE y responde con "
                "conocimiento general, dejandolo claro."
            )
        else:
            context_block = "\n\n".join(
                f"[{r.chunk.source_document} - {r.chunk.article_label}]\n{r.chunk.text}"
                for r in retrieved
            )
            prompt = (
                f"Pregunta: {question}\n\n"
                f"Fragmentos de normativa recuperados:\n{context_block}\n\n"
                "Responda la pregunta siguiendo las instrucciones del sistema."
            )

        answer = self._rag_port.generate(prompt, system=_SYSTEM_PROMPT, max_tokens=600)
        return ChatAnswer(answer=answer, citations=citations)
