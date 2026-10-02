from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import Practice, PracticeStatus
from app.domain.exceptions import NotFoundError


class GetPracticeUseCase:
    """GetPractice (Prompt Maestro §8). Una practica no publicada solo es visible para
    quien tiene practice:read (area de administracion), nunca para el area publica."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, slug: str, actor: User | None) -> Practice:
        with self._uow_factory() as uow:
            practice = uow.practices.get_by_slug(slug)

        if practice is None:
            raise NotFoundError("Practice", slug)

        can_preview_draft = actor is not None and actor.has_permission(perm.PRACTICE_READ)
        if practice.status != PracticeStatus.PUBLISHED and not can_preview_draft:
            raise NotFoundError("Practice", slug)

        return practice
