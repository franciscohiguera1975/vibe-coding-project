import json
from collections.abc import Callable
from pathlib import Path

from app.application.ports.rag import EmbeddingPort, RagPort
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.rag import RagEvaluationRun
from app.domain.exceptions import PermissionDeniedError
from app.domain.services.rag_retrieval import retrieve_top_k

# apps/backend/app/application/use_cases/rag/run_evaluation.py -> apps/backend
_BACKEND_DIR = Path(__file__).resolve().parents[4]
DEFAULT_EVAL_SET_PATH = _BACKEND_DIR / "scripts" / "rag" / "data" / "eval_set.jsonl"

_BASELINE_SYSTEM_PROMPT = (
    "Eres un asistente que responde preguntas sobre la normativa academica de la "
    "Universidad UTE. Responda de la forma mas precisa que pueda con su "
    "conocimiento general, indicando el articulo y documento exacto si lo conoce."
)
_RAG_SYSTEM_PROMPT = (
    "Eres un asistente que responde preguntas sobre la normativa academica de la "
    "UTE, fundamentado estrictamente en los fragmentos de normativa entregados "
    "como contexto. Cite siempre el articulo y el documento exacto de donde "
    "proviene la respuesta; si el contexto no alcanza para responder, diga que no "
    "encontro la normativa aplicable en vez de inventar una respuesta."
)


def _load_eval_set(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"No se encontro el set de evaluacion en {path}")
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


class RunRagEvaluationUseCase:
    """RunRagEvaluation (docs/saturdays_ai/00-plan.md §6): corre el set de ~15
    preguntas de scripts/rag/data/eval_set.jsonl por dos caminos — baseline (el
    LLM responde solo con la pregunta, sin recuperacion) y RAG (recupera top-3
    chunks y los pasa como contexto, igual mecanismo que ValidateSyllabusUseCase)
    — y persiste la comparacion para la pantalla "Evaluacion". El baseline nunca
    puede acertar una cita porque no recibe ninguna: su `baseline_citation_match`
    es siempre False, ese es justamente el punto de la comparacion."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        embedding_port: EmbeddingPort,
        rag_port: RagPort,
        eval_set_path: Path = DEFAULT_EVAL_SET_PATH,
    ) -> None:
        self._uow_factory = uow_factory
        self._embedding_port = embedding_port
        self._rag_port = rag_port
        self._eval_set_path = eval_set_path

    def execute(self, *, actor: User) -> RagEvaluationRun:
        if not actor.has_permission(perm.PRACTICE_UPDATE):
            raise PermissionDeniedError(perm.PRACTICE_UPDATE)

        questions = _load_eval_set(self._eval_set_path)

        with self._uow_factory() as uow:
            all_chunks = uow.normativa_chunks.list_all()

        results: list[dict] = []
        rag_matches = 0
        for question in questions:
            results.append(self._evaluate_question(question, all_chunks))
            if results[-1]["rag_citation_match"]:
                rag_matches += 1

        summary = {
            "total": len(questions),
            "rag_citation_matches": rag_matches,
            "baseline_citation_matches": 0,
        }
        run = RagEvaluationRun(results=results, summary=summary)
        with self._uow_factory() as uow:
            saved = uow.rag_evaluation_runs.add(run)
            uow.commit()
        return saved

    def _evaluate_question(self, question: dict, all_chunks) -> dict:
        baseline_answer = self._rag_port.generate(
            question["question"], system=_BASELINE_SYSTEM_PROMPT, max_tokens=300
        )

        query_embedding = self._embedding_port.embed(question["question"])
        retrieved = retrieve_top_k(query_embedding, all_chunks, k=3)
        context_block = "\n\n".join(
            f"[{r.chunk.source_document} - {r.chunk.article_label}]\n{r.chunk.text}"
            for r in retrieved
        )
        rag_prompt = (
            f"Pregunta: {question['question']}\n\n"
            f"Fragmentos de normativa recuperados:\n{context_block or '(ninguno encontrado)'}\n\n"
            "Responda la pregunta citando el articulo y documento exacto."
        )
        rag_answer = self._rag_port.generate(rag_prompt, system=_RAG_SYSTEM_PROMPT, max_tokens=300)

        expected = question["expected_citation"]
        rag_citation_match = any(
            r.chunk.source_document == expected["source_document"]
            and r.chunk.article_label == expected["article_label"]
            for r in retrieved
        )

        return {
            "id": question["id"],
            "question": question["question"],
            "expected_citation": expected,
            "baseline_answer": baseline_answer,
            "rag_answer": rag_answer,
            "rag_citation_match": rag_citation_match,
            "baseline_citation_match": False,
        }
