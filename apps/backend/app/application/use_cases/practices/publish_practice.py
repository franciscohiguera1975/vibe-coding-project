import uuid
from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import Practice, PracticeStatus
from app.domain.exceptions import NotFoundError, PermissionDeniedError, ValidationError


class PublishPracticeUseCase:
    """PublishPractice (Prompt Maestro §8): exige contenido minimo antes de publicar."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, practice_id: uuid.UUID) -> Practice:
        if not actor.has_permission(perm.PRACTICE_PUBLISH):
            raise PermissionDeniedError(perm.PRACTICE_PUBLISH)

        with self._uow_factory() as uow:
            practice = uow.practices.get_by_id(practice_id)
            if practice is None:
                raise NotFoundError("Practice", str(practice_id))

            if not practice.instructions.strip():
                raise ValidationError("No se puede publicar una practica sin instrucciones")
            if not practice.content:
                raise ValidationError("No se puede publicar una practica sin contenido")

            practice.status = PracticeStatus.PUBLISHED
            updated = uow.practices.update(practice)
            uow.commit()
            return updated
