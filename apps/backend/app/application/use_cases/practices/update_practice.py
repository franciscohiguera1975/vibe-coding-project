import uuid
from collections.abc import Callable

from app.application.dto.practice_dto import UpdatePracticeInput
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import Practice, PracticeDifficulty
from app.domain.exceptions import NotFoundError, PermissionDeniedError
from app.domain.value_objects.slug import Slug


class UpdatePracticeUseCase:
    """UpdatePractice (Prompt Maestro §8): actualizacion parcial, solo los campos provistos."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(
        self, *, actor: User, practice_id: uuid.UUID, data: UpdatePracticeInput
    ) -> Practice:
        if not actor.has_permission(perm.PRACTICE_UPDATE):
            raise PermissionDeniedError(perm.PRACTICE_UPDATE)

        with self._uow_factory() as uow:
            practice = uow.practices.get_by_id(practice_id)
            if practice is None:
                raise NotFoundError("Practice", str(practice_id))

            if data.title is not None:
                practice.title = data.title
            if data.description is not None:
                practice.description = data.description
            if data.objectives is not None:
                practice.objectives = list(data.objectives)
            if data.instructions is not None:
                practice.instructions = data.instructions
            if data.category_slug is not None:
                category = uow.practice_categories.get_by_slug(data.category_slug)
                practice.category_id = category.id if category else None
            if data.difficulty is not None:
                practice.difficulty = PracticeDifficulty(data.difficulty)
            if data.estimated_time_minutes is not None:
                practice.estimated_time_minutes = data.estimated_time_minutes
            if data.technologies is not None:
                practice.technologies = list(data.technologies)
            if data.tag_names is not None:
                tags = [
                    uow.practice_tags.get_or_create(name=name, slug=str(Slug.from_text(name)))
                    for name in data.tag_names
                ]
                practice.tag_ids = [t.id for t in tags]
            if data.content is not None:
                practice.content = dict(data.content)
            if data.evaluation is not None:
                practice.evaluation = dict(data.evaluation)
            if data.ai_configuration is not None:
                practice.ai_configuration = dict(data.ai_configuration)
            if data.embedding_configuration is not None:
                practice.embedding_configuration = dict(data.embedding_configuration)
            if data.metadata is not None:
                practice.metadata = dict(data.metadata)

            updated = uow.practices.update(practice)
            uow.commit()
            return updated
