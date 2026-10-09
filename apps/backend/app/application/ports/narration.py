from typing import Protocol


class NarrationPort(Protocol):
    """Puerto de narracion TTS (texto a voz), analogo a AIProvider (Prompt Maestro
    §10). Las implementaciones concretas (MockNarrationAdapter,
    ElevenLabsNarrationAdapter) viven en infrastructure/ai."""

    def synthesize(self, text: str, *, lang: str) -> bytes:
        """Sintetiza `text` en el idioma `lang` y devuelve el audio (MP3) en bytes."""
        ...
