from dataclasses import dataclass, field
from typing import Any, Protocol

from app.domain.entities.practice import Practice


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    score: float
    passed: bool
    feedback: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class EvaluationPort(Protocol):
    """Puerto de evaluacion (Prompt Maestro §7). Dado el `evaluation` configurado en la
    practica y el envio del estudiante, produce un resultado objetivo (sin IA) que luego
    puede enriquecerse con feedback generado por AIProvider."""

    def evaluate(
        self, *, practice: Practice, submission_payload: dict[str, Any]
    ) -> EvaluationResult: ...
