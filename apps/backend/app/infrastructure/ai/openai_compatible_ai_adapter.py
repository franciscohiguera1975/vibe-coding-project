"""OpenAICompatibleAiAdapter: implementacion real de AIProvider (el puerto del AI
Tutor) contra cualquier endpoint compatible con la API de chat completions de
OpenAI — pensado en primer lugar para vLLM en el HPC de CEDIA, igual patron que
OpenAICompatibleRagAdapter (puerto independiente, ver docs/saturdays_ai/00-plan.md
§3 y §5: AIProvider y RagPort nunca comparten codigo, aunque en produccion puedan
terminar apuntando al mismo vLLM via variables de entorno).

`analyze_image` necesita un modelo con vision (p.ej. Qwen2.5-VL), casi siempre
distinto del modelo de texto — por eso toma su propia base_url/modelo, opcionales:
si no se configuran, analyze_image falla explicitamente en vez de degradar en
silencio (a diferencia del grounding opcional de GenerateAIHintUseCase, un fallo
aqui es la unica senal de que falta ese modelo)."""

import base64
import json

import httpx

from app.application.ports.ai_provider import ImageAnalysisResult
from app.domain.exceptions import ExternalServiceError

_IMAGE_ANALYSIS_INSTRUCTIONS = """Responda UNICAMENTE con un objeto JSON con esta forma exacta,
sin texto adicional ni bloques de codigo: {{"count": <entero>, "confidence": <0 a 1>,
"reason": "<motivo breve>", "illegible": <true|false>}}. No infiera propiedades que la
imagen no permita observar.

Regla de conteo: {instructions}"""


class OpenAICompatibleAiAdapter:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        chat_model: str,
        *,
        vision_base_url: str = "",
        vision_model: str = "",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._chat_model = chat_model
        self._vision_base_url = vision_base_url.rstrip("/") if vision_base_url else ""
        self._vision_model = vision_model

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def _chat(self, base_url: str, model: str, messages: list[dict], max_tokens: int) -> str:
        try:
            response = httpx.post(
                f"{base_url}/chat/completions",
                headers=self._headers(),
                json={"model": model, "messages": messages, "max_tokens": max_tokens},
                timeout=120.0,
            )
        except httpx.HTTPError as exc:
            raise ExternalServiceError("ai_tutor_llm", str(exc)) from exc
        if not response.is_success:
            raise ExternalServiceError(
                "ai_tutor_llm", f"HTTP {response.status_code}: {response.text[:300]}"
            )
        data = response.json()
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError(
                "ai_tutor_llm", f"Respuesta de chat completions con forma inesperada: {data!r}"
            ) from exc

    def generate_text(
        self, prompt: str, *, system: str | None = None, max_tokens: int = 1000
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self._chat(self._base_url, self._chat_model, messages, max_tokens)

    def generate_feedback(self, *, context: dict) -> str:
        prompt = (
            "Redacte una retroalimentacion breve y constructiva para un estudiante, en "
            "espanol, a partir de este contexto de evaluacion (JSON): "
            f"{json.dumps(context, ensure_ascii=False)}. No afirme nada que el contexto "
            "no respalde."
        )
        return self.generate_text(prompt, system="Eres un tutor educativo conciso.", max_tokens=400)

    def analyze_image(
        self, image_bytes: bytes, *, instructions: str, content_type: str
    ) -> ImageAnalysisResult:
        if not self._vision_base_url or not self._vision_model:
            raise ExternalServiceError(
                "ai_tutor_vision",
                "Analisis de imagen requiere AI_VISION_BASE_URL y AI_VISION_MODEL "
                "configurados (modelo con vision, p.ej. Qwen2.5-VL, distinto del "
                "modelo de texto)",
            )
        encoded = base64.b64encode(image_bytes).decode("ascii")
        prompt = _IMAGE_ANALYSIS_INSTRUCTIONS.format(instructions=instructions)
        content = self._chat(
            self._vision_base_url,
            self._vision_model,
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{content_type};base64,{encoded}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            300,
        )
        try:
            parsed = json.loads(content)
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
                details={"raw_response": content},
            )
