from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.application.services import audit
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import PracticeCategory, PracticeTag
from app.domain.exceptions import ConflictError, PermissionDeniedError
from app.domain.value_objects.slug import Slug


class CreatePracticeCategoryUseCase:
    """ManageCatalog (Prompt Maestro §8): alta de categorias del catalogo."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, name: str, slug: str | None = None) -> PracticeCategory:
        if not actor.has_permission(perm.PRACTICE_CREATE):
            raise PermissionDeniedError(perm.PRACTICE_CREATE)

        resolved_slug = str(Slug(slug) if slug else Slug.from_text(name))

        with self._uow_factory() as uow:
            if uow.practice_categories.get_by_slug(resolved_slug) is not None:
                raise ConflictError(f"Ya existe una categoria con el slug {resolved_slug!r}")

            created = uow.practice_categories.add(PracticeCategory(name=name, slug=resolved_slug))
            audit.record(
                uow,
                actor=actor,
                action="catalog.create_category",
                entity_type="PracticeCategory",
                entity_id=str(created.id),
                metadata={"name": name, "slug": resolved_slug},
            )
            uow.commit()
            return created


class CreatePracticeTagUseCase:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, name: str) -> PracticeTag:
        if not actor.has_permission(perm.PRACTICE_CREATE):
            raise PermissionDeniedError(perm.PRACTICE_CREATE)

        with self._uow_factory() as uow:
            tag = uow.practice_tags.get_or_create(name=name, slug=str(Slug.from_text(name)))
            uow.commit()
            return tag
