import json
import re
from collections.abc import Callable
from pathlib import Path

from app.application.ports.rag import EmbeddingPort, RagPort
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.rag import RagEvaluationRun
from app.domain.exceptions import PermissionDeniedError

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


def _mentions_expected_article(answer: str, article_label: str) -> bool:
    """El baseline no recibe ningun fragmento recuperado, asi que solo puede
    citar el articulo correcto si lo conoce de su propio entrenamiento (nunca
    por recuperacion) — por eso esta verificacion es textual, no estructural
    como `rag_citation_match`. Extrae el numero del articulo esperado
    (`article_label` viene como "Articulo 67" o "Art. 1") y busca una mencion
    equivalente en la respuesta libre del LLM, sin exigir el formato exacto
    del corpus (acentos, abreviatura, puntuacion)."""
    match = re.search(r"\d+", article_label)
    if not match:
        return False
    number = re.escape(match.group(0))
    pattern = rf"\bart[íi]culo\.?\s*{number}\b|\bart\.?\s*{number}\b"
    return bool(re.search(pattern, answer, re.IGNORECASE))


class RunRagEvaluationUseCase:
    """RunRagEvaluation (docs/saturdays_ai/00-plan.md §6): corre el set de ~15
    preguntas de scripts/rag/data/eval_set.jsonl por dos caminos — baseline (el
    LLM responde solo con la pregunta, sin recuperacion) y RAG (recupera top-3
    chunks y los pasa como contexto, igual mecanismo que ValidateSyllabusUseCase)
    — y persiste la comparacion para la pantalla "Evaluacion". Las dos metricas
    miden cosas distintas a proposito: `rag_citation_match` es estructural (¿el
    chunk recuperado es el correcto?), mientras que `baseline_citation_match` es
    textual (¿la respuesta libre del LLM, sin ningun contexto, menciona el
    articulo correcto porque ya lo sabia de su entrenamiento?) — ver
    `_mentions_expected_article`."""

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

        results: list[dict] = []
        rag_matches = 0
        baseline_matches = 0
        for question in questions:
            results.append(self._evaluate_question(question))
            if results[-1]["rag_citation_match"]:
                rag_matches += 1
            if results[-1]["baseline_citation_match"]:
                baseline_matches += 1

        summary = {
            "total": len(questions),
            "rag_citation_matches": rag_matches,
            "baseline_citation_matches": baseline_matches,
        }
        run = RagEvaluationRun(results=results, summary=summary)
        with self._uow_factory() as uow:
            saved = uow.rag_evaluation_runs.add(run)
            uow.commit()
        return saved

    def _evaluate_question(self, question: dict) -> dict:
        baseline_answer = self._rag_port.generate(
            question["question"], system=_BASELINE_SYSTEM_PROMPT, max_tokens=300
        )

        query_embedding = self._embedding_port.embed(question["question"], is_query=True)
        with self._uow_factory() as uow:
            retrieved = uow.normativa_chunks.search_hybrid(
                query_embedding, question["question"], k=3
            )
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
        baseline_citation_match = _mentions_expected_article(
            baseline_answer, expected["article_label"]
        )

        return {
            "id": question["id"],
            "question": question["question"],
            "expected_citation": expected,
            "baseline_answer": baseline_answer,
            "rag_answer": rag_answer,
            "rag_citation_match": rag_citation_match,
            "baseline_citation_match": baseline_citation_match,
        }
