"""OpenAICompatibleRagAdapter: implementacion real de RagPort (generacion) contra
cualquier endpoint compatible con la API de chat completions de OpenAI. Pensado en
primer lugar para apuntar a un vLLM corrido en el HPC de CEDIA, tunelado al VPS
via SSH inverso (ver docs/saturdays_ai/02-hpc-pasos.md); intercambiable por
GitHub Models u otro proveedor compatible cambiando solo RAG_BASE_URL/RAG_API_KEY,
sin tocar codigo (docs/saturdays_ai/00-plan.md §5). Usa httpx, igual que
ElevenLabsNarrationAdapter. Nunca se usa en pruebas (ver MockRagAdapter)."""

import httpx

from app.domain.exceptions import ExternalServiceError


class OpenAICompatibleRagAdapter:
    def __init__(self, base_url: str, api_key: str, chat_model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._chat_model = chat_model

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 1000) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = httpx.post(
                f"{self._base_url}/chat/completions",
                headers=self._headers(),
                json={
                    "model": self._chat_model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
                timeout=120.0,
            )
        except httpx.HTTPError as exc:
            raise ExternalServiceError("rag_llm", str(exc)) from exc

        if not response.is_success:
            raise ExternalServiceError(
                "rag_llm", f"HTTP {response.status_code}: {response.text[:300]}"
            )
        data = response.json()
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError(
                "rag_llm", f"Respuesta de chat completions con forma inesperada: {data!r}"
            ) from exc
