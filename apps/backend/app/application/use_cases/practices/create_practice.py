from collections.abc import Callable

from app.application.dto.practice_dto import CreatePracticeInput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import Practice, PracticeDifficulty
from app.domain.exceptions import ConflictError, PermissionDeniedError
from app.domain.value_objects.slug import Slug


class CreatePracticeUseCase:
    """CreatePractice (Prompt Maestro §8, §16)."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, data: CreatePracticeInput) -> Practice:
        if not actor.has_permission(perm.PRACTICE_CREATE):
            raise PermissionDeniedError(perm.PRACTICE_CREATE)

        slug = str(Slug(data.slug) if data.slug else Slug.from_text(data.title))

        with self._uow_factory() as uow:
            if uow.practices.get_by_slug(slug) is not None:
                raise ConflictError(f"Ya existe una practica con el slug {slug!r}")

            category_id = None
            if data.category_slug:
                category = uow.practice_categories.get_by_slug(data.category_slug)
                category_id = category.id if category else None

            tags = [
                uow.practice_tags.get_or_create(name=name, slug=str(Slug.from_text(name)))
                for name in data.tag_names
            ]

            practice = Practice(
                slug=slug,
                title=data.title,
                type=data.type,
                description=data.description,
                objectives=list(data.objectives),
                instructions=data.instructions,
                category_id=category_id,
                difficulty=PracticeDifficulty(data.difficulty),
                estimated_time_minutes=data.estimated_time_minutes,
                technologies=list(data.technologies),
                tag_ids=[t.id for t in tags],
                content=dict(data.content),
                evaluation=dict(data.evaluation),
                ai_configuration=dict(data.ai_configuration),
                embedding_configuration=dict(data.embedding_configuration),
                metadata=dict(data.metadata),
                translations=dict(data.translations),
                created_by_id=actor.id,
            )
            created = uow.practices.add(practice)
            uow.commit()
            return created
