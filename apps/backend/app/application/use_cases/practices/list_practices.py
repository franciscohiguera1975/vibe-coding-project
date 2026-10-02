from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import Practice, PracticeStatus
from app.domain.repositories.practice_repository import PracticeFilters
from app.domain.value_objects.pagination import Page, PageRequest


class ListPracticesUseCase:
    """ListPractices (Prompt Maestro §8, §14): catalogo publico filtrable por categoria,
    nivel, tecnologia, tipo, IA e imagenes. Sin permiso practice:read solo ve publicadas."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(
        self, *, actor: User | None, filters: PracticeFilters, page_request: PageRequest
    ) -> Page[Practice]:
        can_see_all_statuses = actor is not None and actor.has_permission(perm.PRACTICE_READ)
        if not can_see_all_statuses:
            filters = PracticeFilters(
                category_id=filters.category_id,
                difficulty=filters.difficulty,
                technology=filters.technology,
                type=filters.type,
                status=PracticeStatus.PUBLISHED,
                has_ai=filters.has_ai,
                search=filters.search,
            )

        with self._uow_factory() as uow:
            return uow.practices.list(filters, page_request)
