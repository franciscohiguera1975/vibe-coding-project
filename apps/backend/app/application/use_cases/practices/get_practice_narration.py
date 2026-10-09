from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import PracticeNarration, PracticeStatus
from app.domain.exceptions import NotFoundError


class GetPracticeNarrationUseCase:
    """GetPracticeNarration: lectura publica (misma visibilidad que GetPractice: una
    practica no publicada solo es visible para quien tiene practice:read) del audio
    narrado ya generado para una practica e idioma. No genera nada — si no existe un
    registro, el llamador (router) debe responder 404."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, slug: str, lang: str, actor: User | None = None) -> PracticeNarration:
        with self._uow_factory() as uow:
            practice = uow.practices.get_by_slug(slug)
            if practice is None:
                raise NotFoundError("Practice", slug)

            can_preview_draft = actor is not None and actor.has_permission(perm.PRACTICE_READ)
            if practice.status != PracticeStatus.PUBLISHED and not can_preview_draft:
                raise NotFoundError("Practice", slug)

            narration = uow.practice_narrations.get_by_practice_and_lang(practice.id, lang)
            if narration is None:
                raise NotFoundError("PracticeNarration", f"{slug}:{lang}")
            return narration
