"""TeiEmbeddingAdapter: implementacion real de EmbeddingPort contra un servidor
Text Embeddings Inference (Hugging Face) corrido en el HPC de CEDIA, tunelado al
VPS via SSH inverso (ver docs/saturdays_ai/02-hpc-pasos.md). Mismo patron que
OpenAICompatibleRagAdapter (httpx, ExternalServiceError en fallos). Nunca se usa
en pruebas (ver MockRagAdapter)."""

import httpx

from app.domain.exceptions import ExternalServiceError


class TeiEmbeddingAdapter:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def embed(self, text: str) -> list[float]:
        try:
            response = httpx.post(
                f"{self._base_url}/embed",
                headers={"Content-Type": "application/json"},
                json={"inputs": text},
                timeout=60.0,
            )
        except httpx.HTTPError as exc:
            raise ExternalServiceError("tei_embeddings", str(exc)) from exc

        if not response.is_success:
            raise ExternalServiceError(
                "tei_embeddings", f"HTTP {response.status_code}: {response.text[:300]}"
            )
        data = response.json()
        try:
            # TEI /embed siempre devuelve una lista de vectores (uno por texto de
            # entrada); con una sola cadena de entrada, el primero es el nuestro.
            return list(data[0])
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError(
                "tei_embeddings", f"Respuesta de /embed con forma inesperada: {data!r}"
            ) from exc
