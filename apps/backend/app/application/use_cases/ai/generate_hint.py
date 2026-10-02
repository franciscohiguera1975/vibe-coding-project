from collections.abc import Callable

from app.application.ports.ai_provider import AIProvider
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.domain.exceptions import NotFoundError

_HINT_SYSTEM_PROMPT = (
    "Eres un tutor de un curso de Vibe Coding. Da una pista breve que oriente al "
    "estudiante hacia la solucion sin revelarla por completo ni inventar informacion "
    "que no este en las instrucciones de la practica."
)


class GenerateAIHintUseCase:
    """GenerateAIHint (Prompt Maestro §8, §11): una pista por practica, nunca la
    respuesta exacta. Cualquier usuario autenticado puede pedir una pista."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], ai_provider: AIProvider) -> None:
        self._uow_factory = uow_factory
        self._ai_provider = ai_provider

    def execute(self, *, actor: User, practice_slug: str, student_context: str = "") -> str:
        with self._uow_factory() as uow:
            practice = uow.practices.get_by_slug(practice_slug)
        if practice is None:
            raise NotFoundError("Practice", practice_slug)

        prompt = (
            f"Practica: {practice.title}\n"
            f"Instrucciones: {practice.instructions}\n"
            f"Contenido: {practice.content}\n"
            f"Lo que el estudiante ha intentado hasta ahora: {student_context or 'nada aun'}\n"
            "Genere una pista."
        )
        return self._ai_provider.generate_text(prompt, system=_HINT_SYSTEM_PROMPT, max_tokens=300)
