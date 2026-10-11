import pytest

from app.application.use_cases.rag.run_evaluation import _mentions_expected_article


@pytest.mark.parametrize(
    "answer",
    [
        "Según el Artículo 67 del Reglamento, los docentes deben...",
        "segun el articulo 67 del reglamento",  # sin acentos ni mayusculas
        "Ver Art. 67 para el detalle.",
        "Ver Art 67 para el detalle.",  # sin punto
    ],
)
def test_mentions_expected_article_matches_equivalent_formats(answer):
    assert _mentions_expected_article(answer, "Artículo 67") is True


@pytest.mark.parametrize(
    "answer",
    [
        "Según el Artículo 68 del Reglamento, los docentes deben...",  # numero distinto
        "No tengo informacion suficiente para responder con precision.",
        "El articulo 670 no aplica aqui.",  # 670 no es 67 (limite de palabra)
    ],
)
def test_mentions_expected_article_rejects_non_matches(answer):
    assert _mentions_expected_article(answer, "Artículo 67") is False


def test_mentions_expected_article_handles_label_without_digits():
    assert _mentions_expected_article("cualquier respuesta", "Disposición General") is False
