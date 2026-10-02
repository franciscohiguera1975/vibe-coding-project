from collections.abc import Callable

from app.application.ports.ai_provider import AIProvider, ImageAnalysisResult
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import NotFoundError


class AnalyzeImageUseCase:
    """AnalyzeImage (Prompt Maestro §8, §10): aplica la regla de conteo de la
    practica (practice.content.counting_rule) sobre una imagen ya validada."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], ai_provider: AIProvider) -> None:
        self._uow_factory = uow_factory
        self._ai_provider = ai_provider

    def execute(
        self, *, practice_slug: str, file_bytes: bytes, content_type: str
    ) -> ImageAnalysisResult:
        with self._uow_factory() as uow:
            practice = uow.practices.get_by_slug(practice_slug)
        if practice is None:
            raise NotFoundError("Practice", practice_slug)

        counting_rule = practice.content.get("counting_rule", {}) if practice.content else {}
        instructions = (
            f"Cuenta: {counting_rule.get('counts', 'objetos visibles')}. "
            f"No cuenta: {', '.join(counting_rule.get('excludes', []))}. "
            f"Ilegible cuando: {', '.join(counting_rule.get('illegible_when', []))}."
        )
        return self._ai_provider.analyze_image(
            file_bytes, instructions=instructions, content_type=content_type
        )
