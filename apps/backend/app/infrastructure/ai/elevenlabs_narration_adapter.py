"""ElevenLabsNarrationAdapter: implementacion real de NarrationPort sobre la API de
ElevenLabs. Se activa con NARRATION_PROVIDER=elevenlabs y ELEVENLABS_API_KEY en el
entorno; nunca se usa en pruebas (ver MockNarrationAdapter). Usa httpx, el mismo
cliente HTTP que ya trae el proyecto como dependencia (y que usa el SDK `anthropic`
bajo el capo para AnthropicAdapter), para no introducir una libreria nueva."""

import httpx

from app.domain.exceptions import ExternalServiceError

_BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"


class ElevenLabsNarrationAdapter:
    def __init__(self, api_key: str, voice_id: str, model_id: str) -> None:
        self._api_key = api_key
        self._voice_id = voice_id
        self._model_id = model_id

    def synthesize(self, text: str, *, lang: str) -> bytes:
        url = f"{_BASE_URL}/{self._voice_id}"
        try:
            response = httpx.post(
                url,
                headers={"xi-api-key": self._api_key},
                json={
                    "text": text,
                    "model_id": self._model_id,
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                },
                timeout=60.0,
            )
        except httpx.HTTPError as exc:
            raise ExternalServiceError("elevenlabs", str(exc)) from exc

        if not response.is_success:
            raise ExternalServiceError(
                "elevenlabs", f"HTTP {response.status_code}: {response.text[:300]}"
            )
        return response.content
