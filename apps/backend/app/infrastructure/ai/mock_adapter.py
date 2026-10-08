"""MockAIAdapter (Prompt Maestro §10): implementacion de AIProvider sin llamadas de
red, usada por defecto en desarrollo y siempre en pruebas (AI_PROVIDER=mock). Genera
texto determinista a partir del contexto recibido — suficiente para ejercitar el
flujo completo (pistas, feedback, analisis de imagen) sin depender de un proveedor
externo ni de credenciales."""

from typing import Any

from app.application.ports.ai_provider import ImageAnalysisResult


class MockAIAdapter:
    def generate_text(
        self, prompt: str, *, system: str | None = None, max_tokens: int = 1000
    ) -> str:
        prefix = f"[{system}] " if system else ""
        snippet = prompt.strip().splitlines()[0][:160] if prompt.strip() else ""
        return f"{prefix}Respuesta simulada para: {snippet}"

    def analyze_image(
        self, image_bytes: bytes, *, instructions: str, content_type: str
    ) -> ImageAnalysisResult:
        """Heuristica determinista (no IA real): cuenta regiones conectadas de color
        saturado sobre fondo claro, acorde a la regla de la Guia 02 (circulos de papel
        de colores). Sirve de referencia local/offline; AnthropicAdapter usa vision
        real cuando AI_PROVIDER=anthropic."""
        from app.infrastructure.ai.image_counting import count_colored_regions

        if not image_bytes:
            return ImageAnalysisResult(count=0, warnings=["imagen vacia"], details={})
        try:
            count, details = count_colored_regions(image_bytes)
        except Exception as exc:  # noqa: BLE001 - cualquier imagen no decodificable es "ilegible"
            return ImageAnalysisResult(
                count=0, warnings=[f"imagen ilegible: {exc}"], details={"illegible": True}
            )
        # Una escena vacia (conteo 0 con imagen nitida) es un resultado valido, no una
        # advertencia: la regla de la guia distingue "vacia" (cuenta 0, sin aviso) de
        # "borrosa" (ilegible, con aviso) — confundirlas produciria una advertencia falsa.
        warnings = (
            ["imagen ilegible: desenfoque impide distinguir los centros"]
            if details.get("illegible")
            else []
        )
        return ImageAnalysisResult(count=count, warnings=warnings, details=details)

    def generate_feedback(self, *, context: dict[str, Any]) -> str:
        score = context.get("score")
        passed = context.get("passed")
        practice_title = context.get("practice_title", "la practica")
        if passed is True:
            return (
                f"Buen trabajo en {practice_title}. Su envio cumplio los criterios "
                f"evaluados (puntaje {score}). Revise el detalle para confirmar que "
                "entiende por que cada caso paso."
            )
        if passed is False:
            return (
                f"Su envio para {practice_title} no cumplio todos los criterios "
                f"(puntaje {score}). Revise los casos marcados como incorrectos en el "
                "detalle de la evaluacion y compare con las instrucciones antes de "
                "reintentar."
            )
        return (
            f"Su envio para {practice_title} quedo registrado para revision manual. "
            "Un docente revisara el contenido enviado."
        )
