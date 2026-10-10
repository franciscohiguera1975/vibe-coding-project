"""MockRagAdapter: implementacion de RagPort sin llamadas de red, usada por
defecto en desarrollo y siempre en pruebas (RAG_LLM_PROVIDER=mock), igual patron
que MockAIAdapter/MockNarrationAdapter. `embed` deriva un vector pseudo-aleatorio
PERO DETERMINISTA de dimension fija a partir de un hash del texto (textos iguales
-> mismo vector, asi la similitud de coseno es reproducible en pruebas); `generate`
devuelve una respuesta enlatada determinista, igual que MockAIAdapter.generate_text."""

import hashlib

EMBEDDING_DIMENSIONS = 128


class MockRagAdapter:
    def embed(self, text: str, *, is_query: bool = False) -> list[float]:
        normalized = text.strip().lower()
        vector: list[float] = []
        counter = 0
        while len(vector) < EMBEDDING_DIMENSIONS:
            digest = hashlib.sha256(f"{counter}:{normalized}".encode("utf-8")).digest()
            for byte in digest:
                # Mapea cada byte (0-255) a [-1, 1] para tener un vector denso
                # "normal-ish", sin depender de numpy.
                vector.append((byte / 127.5) - 1.0)
                if len(vector) >= EMBEDDING_DIMENSIONS:
                    break
            counter += 1
        return vector

    def generate(self, prompt: str, *, system: str | None = None, max_tokens: int = 1000) -> str:
        prefix = f"[{system}] " if system else ""
        snippet = prompt.strip().splitlines()[0][:160] if prompt.strip() else ""
        return f"{prefix}Respuesta simulada (RAG mock) para: {snippet}"
