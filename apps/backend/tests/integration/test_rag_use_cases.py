import json

import pytest

from app.application.use_cases.rag.run_evaluation import RunRagEvaluationUseCase
from app.application.use_cases.rag.validate_syllabus import ValidateSyllabusUseCase
from app.domain.entities.rag import NormativaChunk
from app.domain.exceptions import PermissionDeniedError
from app.domain.services.syllabus_checklist import CHECKLIST_ITEMS
from app.infrastructure.ai.mock_rag_adapter import MockRagAdapter
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def rag_mock() -> MockRagAdapter:
    return MockRagAdapter()


@pytest.fixture
def seeded_chunks(rag_mock: MockRagAdapter) -> list[NormativaChunk]:
    """Un corpus minimo pero real para ejercitar la recuperacion sin depender de
    chunks.jsonl (dato local, gitignored, no disponible en CI)."""
    texts = [
        (
            "chunk-67",
            "Reglamento de Régimen Académico.pdf",
            "Artículo 67",
            "objetivos contenidos rubrica criterios de calificacion medios ambientes instrumentos",
        ),
        (
            "chunk-40",
            "Reglamento del Estudiante.pdf",
            "Artículo 40",
            "recalificacion resultados de aprendizaje incluidos en el silabo",
        ),
        (
            "chunk-35",
            "Reglamento del Estudiante.pdf",
            "Artículo 35",
            "principios evaluacion transparente metodologia",
        ),
    ]
    chunks = []
    with SqlAlchemyUnitOfWork() as uow:
        for chunk_id, doc, label, text in texts:
            chunk = uow.normativa_chunks.upsert(
                NormativaChunk(
                    chunk_id=chunk_id,
                    source_document=doc,
                    article_label=label,
                    text=text,
                    embedding=rag_mock.embed(text),
                )
            )
            chunks.append(chunk)
        uow.commit()
    return chunks


def test_validate_syllabus_returns_one_result_per_checklist_item_with_citations(
    admin_user, rag_mock, seeded_chunks
):
    use_case = ValidateSyllabusUseCase(SqlAlchemyUnitOfWork, rag_mock, rag_mock)
    syllabus_text = (
        "Objetivos: comprender X. Resultados de aprendizaje: aplicar Y. "
        "Contenidos: unidad 1, unidad 2. Metodologia: clases practicas. "
        "Criterios de calificacion: rubrica con 3 niveles."
    )

    results = use_case.execute(actor=admin_user, syllabus_text=syllabus_text)

    assert len(results) == len(CHECKLIST_ITEMS) == 5
    assert {r.item for r in results} == {item.key for item in CHECKLIST_ITEMS}
    for result in results:
        assert len(result.citas) >= 1
        assert result.cumple in (True, False, None)
        assert isinstance(result.explicacion, str) and result.explicacion


def test_validate_syllabus_returns_no_citations_without_loaded_chunks(admin_user, rag_mock):
    use_case = ValidateSyllabusUseCase(SqlAlchemyUnitOfWork, rag_mock, rag_mock)

    results = use_case.execute(actor=admin_user, syllabus_text="un silabo cualquiera")

    assert len(results) == 5
    for result in results:
        assert result.citas == []
        assert result.cumple is None


def test_run_evaluation_scores_rag_and_baseline_citation_matches(
    admin_user, rag_mock, seeded_chunks, tmp_path
):
    # Preguntas controladas: la primera y la tercera piden exactamente el texto de
    # un chunk existente (asi MockRagAdapter.embed, deterministico por hash del
    # texto, produce el mismo vector y la recuperacion las encuentra con score 1.0);
    # la segunda espera una cita que no corresponde a ningun chunk cargado, para
    # verificar que el score de "no coincide" tambien se calcula correctamente.
    # La cuarta ("baseline-hit") verifica `baseline_citation_match`: su propia
    # pregunta menciona el articulo esperado, y MockRagAdapter.generate() hace eco
    # del prompt — asi el baseline "acierta" la cita sin haber recuperado nada,
    # igual que lo haria un LLM real que ya conoce la normativa de memoria. Su
    # `rag_citation_match` tambien da True, pero no porque la recuperacion haya
    # sido buena: con solo 3 chunks sembrados y k=3, `retrieve_top_k` siempre
    # devuelve los 3 (cualquier cita entre esos 3 "acierta" sin importar el
    # ranking) — por eso "mismatch-1" (que pide un documento no cargado) es la
    # unica forma real de ver un `rag_citation_match` en False en este fixture.
    eval_set = [
        {
            "id": "ok-1",
            "question": (
                "objetivos contenidos rubrica criterios de calificacion medios "
                "ambientes instrumentos"
            ),
            "expected_citation": {
                "source_document": "Reglamento de Régimen Académico.pdf",
                "article_label": "Artículo 67",
            },
            "expected_answer_summary": "resumen 1",
        },
        {
            "id": "mismatch-1",
            "question": "pregunta sin relacion con los chunks cargados",
            "expected_citation": {
                "source_document": "Documento que no existe.pdf",
                "article_label": "Artículo 999",
            },
            "expected_answer_summary": "resumen 2",
        },
        {
            "id": "ok-2",
            "question": "recalificacion resultados de aprendizaje incluidos en el silabo",
            "expected_citation": {
                "source_document": "Reglamento del Estudiante.pdf",
                "article_label": "Artículo 40",
            },
            "expected_answer_summary": "resumen 3",
        },
        {
            "id": "baseline-hit",
            "question": "segun el articulo 35, que principios debe garantizar la evaluacion",
            "expected_citation": {
                "source_document": "Reglamento del Estudiante.pdf",
                "article_label": "Artículo 35",
            },
            "expected_answer_summary": "resumen 4",
        },
    ]
    eval_set_path = tmp_path / "eval_set.jsonl"
    eval_set_path.write_text(
        "\n".join(json.dumps(q, ensure_ascii=False) for q in eval_set), encoding="utf-8"
    )

    use_case = RunRagEvaluationUseCase(
        SqlAlchemyUnitOfWork, rag_mock, rag_mock, eval_set_path=eval_set_path
    )
    run = use_case.execute(actor=admin_user)

    assert run.id is not None
    assert run.summary == {"total": 4, "rag_citation_matches": 3, "baseline_citation_matches": 1}

    by_id = {r["id"]: r for r in run.results}
    assert by_id["ok-1"]["rag_citation_match"] is True
    assert by_id["ok-2"]["rag_citation_match"] is True
    assert by_id["mismatch-1"]["rag_citation_match"] is False
    assert by_id["baseline-hit"]["rag_citation_match"] is True
    assert by_id["baseline-hit"]["baseline_citation_match"] is True
    assert by_id["ok-1"]["baseline_citation_match"] is False
    assert by_id["ok-2"]["baseline_citation_match"] is False
    assert by_id["mismatch-1"]["baseline_citation_match"] is False

    persisted = None
    with SqlAlchemyUnitOfWork() as uow:
        persisted = uow.rag_evaluation_runs.get_latest()
    assert persisted is not None
    assert persisted.id == run.id
    assert persisted.summary["rag_citation_matches"] == 3


def test_run_evaluation_requires_permission(student_role, password_hasher, tmp_path):
    from app.domain.entities.identity import User

    with SqlAlchemyUnitOfWork() as uow:
        student = uow.users.add(
            User(
                email="estudiante-rag@vibe-coding-platform.dev",
                password_hash=password_hasher.hash("Student123!"),
                full_name="Estudiante",
                roles=[student_role],
            )
        )
        uow.commit()

    eval_set_path = tmp_path / "eval_set.jsonl"
    eval_set_path.write_text("", encoding="utf-8")
    use_case = RunRagEvaluationUseCase(
        SqlAlchemyUnitOfWork, MockRagAdapter(), MockRagAdapter(), eval_set_path=eval_set_path
    )
    with pytest.raises(PermissionDeniedError):
        use_case.execute(actor=student)
