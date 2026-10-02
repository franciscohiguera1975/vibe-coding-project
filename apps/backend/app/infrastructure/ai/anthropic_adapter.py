"""AnthropicAdapter (Prompt Maestro §10): implementacion real de AIProvider sobre la
API de Claude. Se activa con AI_PROVIDER=anthropic y AI_API_KEY en el entorno; nunca
se usa en pruebas (ver MockAIAdapter)."""

import base64
import json
from typing import Any

from anthropic import Anthropic

from app.application.ports.ai_provider import ImageAnalysisResult

_IMAGE_ANALYSIS_INSTRUCTIONS = """Responda unicamente con un objeto JSON con esta forma exacta,
sin texto adicional: {{"count": <entero>, "confidence": <0 a 1>, "reason": "<motivo breve>",
"illegible": <true|false>}}. No infiera propiedades que la imagen no permita observar.

Regla de conteo: {instructions}"""


class AnthropicAdapter:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def generate_text(
        self, prompt: str, *, system: str | None = None, max_tokens: int = 1000
    ) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")

    def analyze_image(
        self, image_bytes: bytes, *, instructions: str, content_type: str
    ) -> ImageAnalysisResult:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        prompt = _IMAGE_ANALYSIS_INSTRUCTIONS.format(instructions=instructions)
        response = self._client.messages.create(
            model=self._model,
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": content_type,
                                "data": encoded,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        try:
            parsed = json.loads(text)
            count = int(parsed["count"])
            illegible = bool(parsed.get("illegible", False))
            warnings = ["imagen ilegible"] if illegible else []
            return ImageAnalysisResult(
                count=0 if illegible else count,
                warnings=warnings,
                details={
                    "confidence": parsed.get("confidence"),
                    "reason": parsed.get("reason"),
                    "illegible": illegible,
                },
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            return ImageAnalysisResult(
                count=0,
                warnings=["respuesta del modelo no interpretable; tratada como ilegible"],
                details={"raw_response": text},
            )

    def generate_feedback(self, *, context: dict[str, Any]) -> str:
        prompt = (
            "Redacte una retroalimentacion breve y constructiva para un estudiante, en "
            "espanol, a partir de este contexto de evaluacion (JSON): "
            f"{json.dumps(context, ensure_ascii=False)}. No afirme nada que el contexto "
            "no respalde."
        )
        return self.generate_text(prompt, system="Eres un tutor educativo conciso.", max_tokens=400)
