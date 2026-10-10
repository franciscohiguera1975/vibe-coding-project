"""Checklist de contenido obligatorio de un silabo, fundamentado en el Articulo 67
del Reglamento de Regimen Academico ("objetivos, contenidos, rubrica, criterios de
calificacion, medios, ambientes e instrumentos" a difundir via los syllabus) y el
Articulo 40 del Reglamento del Estudiante (resultados de aprendizaje incluidos en
el silabo) — ver docs/saturdays_ai/00-plan.md. Este modulo solo hace la deteccion
heuristica/textual de cada item (no decide "cumple", eso lo hace el LLM grounded
en la normativa real, ver app.application.use_cases.rag.validate_syllabus)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChecklistItem:
    key: str
    label: str
    keywords: tuple[str, ...]


CHECKLIST_ITEMS: tuple[ChecklistItem, ...] = (
    ChecklistItem(
        key="objetivos",
        label="Objetivos",
        keywords=("objetivo", "objetivos", "proposito", "propósito"),
    ),
    ChecklistItem(
        key="resultados_aprendizaje",
        label="Resultados de aprendizaje",
        keywords=("resultado de aprendizaje", "resultados de aprendizaje", "competencia"),
    ),
    ChecklistItem(
        key="contenidos",
        label="Contenidos por unidad/tema",
        keywords=("contenido", "contenidos", "unidad", "unidades", "tema", "temas"),
    ),
    ChecklistItem(
        key="metodologia",
        label="Metodologia",
        keywords=("metodologia", "metodología", "estrategia didactica", "estrategia didáctica"),
    ),
    ChecklistItem(
        key="criterios_calificacion",
        label="Criterios de calificacion / rubrica / instrumentos de evaluacion",
        keywords=(
            "criterio de calificacion",
            "criterios de calificación",
            "rubrica",
            "rúbrica",
            "instrumento de evaluacion",
            "instrumentos de evaluación",
            "sistema de evaluacion",
            "sistema de evaluación",
        ),
    ),
)


def detect_item(item: ChecklistItem, syllabus_text: str) -> bool:
    """Deteccion heuristica por palabra clave (no necesita ser perfecta, ver
    docs/saturdays_ai/00-plan.md: el veredicto real de cumplimiento lo da el LLM
    grounded en la normativa, esto solo informa esa llamada)."""
    haystack = syllabus_text.lower()
    return any(keyword in haystack for keyword in item.keywords)
