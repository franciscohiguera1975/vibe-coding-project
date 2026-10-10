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

    def embed(self, text: str, *, is_query: bool = False) -> list[float]:
        # Convencion de la familia E5 (intfloat/multilingual-e5-large, el modelo
        # usado aqui): sin este prefijo la recuperacion es muy pobre (ver
        # docstring de EmbeddingPort). Si en el futuro se cambia a un modelo que
        # no lo necesita, este prefijo no le hace dano (queda como texto normal).
        prefixed = f"{'query' if is_query else 'passage'}: {text}"
        try:
            response = httpx.post(
                f"{self._base_url}/embed",
                headers={"Content-Type": "application/json"},
                json={"inputs": prefixed},
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
