"""MockNarrationAdapter: implementacion de NarrationPort sin llamadas de red, usada
por defecto en desarrollo y siempre en pruebas (NARRATION_PROVIDER=mock). Genera
bytes deterministas a partir de `(text, lang)` — suficiente para ejercitar el flujo
completo (cache por hash, subida a StoragePort, endpoints) sin depender de
ElevenLabs ni de credenciales."""

import hashlib


class MockNarrationAdapter:
    def synthesize(self, text: str, *, lang: str) -> bytes:
        digest = hashlib.sha256(f"{lang}:{text}".encode()).hexdigest()
        return f"MOCK-MP3:{lang}:{digest}".encode("ascii")
