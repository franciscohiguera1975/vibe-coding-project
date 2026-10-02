from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ImageAnalysisResult:
    """Resultado generico de analizar una imagen (conteo, deteccion, etc.). `details`
    lleva informacion especifica del metodo usado (p.ej. la regla de conteo aplicada)."""

    count: int
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class AIProvider(Protocol):
    """Puerto de IA desacoplada (Prompt Maestro §10). Las implementaciones concretas
    (MockAIAdapter, AnthropicAdapter) viven en infrastructure/ai."""

    def generate_text(
        self, prompt: str, *, system: str | None = None, max_tokens: int = 1000
    ) -> str: ...

    def analyze_image(
        self, image_bytes: bytes, *, instructions: str, content_type: str
    ) -> ImageAnalysisResult: ...

    def generate_feedback(self, *, context: dict[str, Any]) -> str: ...
