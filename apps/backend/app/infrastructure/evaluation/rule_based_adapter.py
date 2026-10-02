"""Adaptador de EvaluationPort basado en reglas explicitas (sin IA), leidas de
`practice.evaluation`. Dos estrategias derivadas directamente de las guias CEDIA:

- "numeric_match": compara valores calculados contra casos esperados (Guia 18 — los
  tres ejemplos numericos de `modelo.md` y la pregunta de transferencia).
- "count_comparison": compara conteos por imagen contra una referencia humana
  (Guia 02 — `referencia.csv` frente a `resultados.csv`).

Cualquier otra estrategia (o ninguna) cae en revision manual explicita en vez de
inventar un resultado."""

from typing import Any

from app.application.ports.evaluation import EvaluationResult
from app.domain.entities.practice import Practice


class RuleBasedEvaluationAdapter:
    def evaluate(
        self, *, practice: Practice, submission_payload: dict[str, Any]
    ) -> EvaluationResult:
        config = practice.evaluation or {}
        strategy = config.get("strategy", "manual")
        if strategy == "numeric_match":
            return self._evaluate_numeric_match(config, submission_payload)
        if strategy == "count_comparison":
            return self._evaluate_count_comparison(config, submission_payload)
        return EvaluationResult(
            score=0,
            passed=False,
            feedback="Esta practica no tiene una regla automatica; requiere revision manual.",
        )

    def _evaluate_numeric_match(
        self, config: dict[str, Any], payload: dict[str, Any]
    ) -> EvaluationResult:
        checks: list[dict[str, Any]] = config.get("checks", [])
        total = len(checks) or 1
        details = []
        correct = 0
        for check in checks:
            field = check["field"]
            expected = check["expected"]
            tolerance = check.get("tolerance", 0)
            actual = payload.get(field)
            ok = actual is not None and abs(actual - expected) <= tolerance
            correct += int(ok)
            details.append({"field": field, "expected": expected, "actual": actual, "ok": ok})

        score = round(100 * correct / total, 2)
        passed = correct == total
        feedback = (
            "Todos los casos coinciden con el modelo."
            if passed
            else f"{correct}/{total} casos coinciden con el modelo."
        )
        return EvaluationResult(
            score=score, passed=passed, feedback=feedback, details={"checks": details}
        )

    def _evaluate_count_comparison(
        self, config: dict[str, Any], payload: dict[str, Any]
    ) -> EvaluationResult:
        reference: dict[str, int] = config.get("reference", {})
        submitted: dict[str, int] = payload.get("counts", {})
        passing_score = config.get("passing_score", 75)
        total = len(reference) or 1
        details = []
        correct = 0
        for image_id, expected_count in reference.items():
            actual = submitted.get(image_id)
            ok = actual == expected_count
            correct += int(ok)
            details.append(
                {"image_id": image_id, "expected": expected_count, "actual": actual, "ok": ok}
            )

        score = round(100 * correct / total, 2)
        passed = score >= passing_score
        feedback = f"{correct}/{total} conteos coinciden con la referencia humana."
        return EvaluationResult(
            score=score, passed=passed, feedback=feedback, details={"images": details}
        )
