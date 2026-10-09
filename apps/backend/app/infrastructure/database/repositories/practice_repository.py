import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.practice import (
    Practice,
    PracticeCategory,
    PracticeDifficulty,
    PracticeNarration,
    PracticeStatus,
    PracticeTag,
)
from app.domain.repositories.practice_repository import PracticeFilters
from app.domain.value_objects.pagination import Page, PageRequest
from app.infrastructure.database.models.catalog import PracticeCategoryModel, PracticeTagModel
from app.infrastructure.database.models.practice import PracticeModel, PracticeNarrationModel


def _category_to_domain(model: PracticeCategoryModel) -> PracticeCategory:
    return PracticeCategory(
        id=model.id,
        name=model.name,
        slug=model.slug,
        description=model.description,
        parent_id=model.parent_id,
    )


def _tag_to_domain(model: PracticeTagModel) -> PracticeTag:
    return PracticeTag(id=model.id, name=model.name, slug=model.slug)


def _practice_to_domain(model: PracticeModel) -> Practice:
    return Practice(
        id=model.id,
        slug=model.slug,
        title=model.title,
        type=model.type,
        description=model.description,
        objectives=list(model.objectives),
        instructions=model.instructions,
        category_id=model.category_id,
        difficulty=PracticeDifficulty(model.difficulty.value),
        estimated_time_minutes=model.estimated_time_minutes,
        technologies=list(model.technologies),
        tag_ids=[t.id for t in model.tags],
        content=dict(model.content),
        evaluation=dict(model.evaluation),
        ai_configuration=dict(model.ai_configuration),
        embedding_configuration=dict(model.embedding_configuration),
        status=PracticeStatus(model.status.value),
        metadata=dict(model.practice_metadata),
        translations=dict(model.translations),
        created_by_id=model.created_by_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyPracticeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_query(self):
        return select(PracticeModel).options(selectinload(PracticeModel.tags))

    def get_by_id(self, practice_id: uuid.UUID) -> Practice | None:
        model = self._session.scalar(self._base_query().where(PracticeModel.id == practice_id))
        return _practice_to_domain(model) if model else None

    def get_by_slug(self, slug: str) -> Practice | None:
        model = self._session.scalar(self._base_query().where(PracticeModel.slug == slug))
        return _practice_to_domain(model) if model else None

    def add(self, practice: Practice) -> Practice:
        tag_models = []
        if practice.tag_ids:
            tag_models = list(
                self._session.scalars(
                    select(PracticeTagModel).where(PracticeTagModel.id.in_(practice.tag_ids))
                )
            )
        model = PracticeModel(
            slug=practice.slug,
            title=practice.title,
            description=practice.description,
            objectives=list(practice.objectives),
            instructions=practice.instructions,
            category_id=practice.category_id,
            difficulty=practice.difficulty,
            estimated_time_minutes=practice.estimated_time_minutes,
            technologies=list(practice.technologies),
            type=practice.type,
            content=dict(practice.content),
            evaluation=dict(practice.evaluation),
            ai_configuration=dict(practice.ai_configuration),
            embedding_configuration=dict(practice.embedding_configuration),
            status=practice.status,
            practice_metadata=dict(practice.metadata),
            translations=dict(practice.translations),
            created_by_id=practice.created_by_id,
            tags=tag_models,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model, attribute_names=["tags"])
        return _practice_to_domain(model)

    def update(self, practice: Practice) -> Practice:
        model = self._session.get(PracticeModel, practice.id)
        if model is None:
            raise ValueError(f"PracticeModel {practice.id} no encontrado")
        model.slug = practice.slug
        model.title = practice.title
        model.description = practice.description
        model.objectives = list(practice.objectives)
        model.instructions = practice.instructions
        model.category_id = practice.category_id
        model.difficulty = practice.difficulty
        model.estimated_time_minutes = practice.estimated_time_minutes
        model.technologies = list(practice.technologies)
        model.type = practice.type
        model.content = dict(practice.content)
        model.evaluation = dict(practice.evaluation)
        model.ai_configuration = dict(practice.ai_configuration)
        model.embedding_configuration = dict(practice.embedding_configuration)
        model.status = practice.status
        model.practice_metadata = dict(practice.metadata)
        model.translations = dict(practice.translations)
        if practice.tag_ids:
            model.tags = list(
                self._session.scalars(
                    select(PracticeTagModel).where(PracticeTagModel.id.in_(practice.tag_ids))
                )
            )
        self._session.flush()
        return _practice_to_domain(model)

    def delete(self, practice_id: uuid.UUID) -> None:
        model = self._session.get(PracticeModel, practice_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def list(self, filters: PracticeFilters, page_request: PageRequest) -> Page[Practice]:
        query = self._base_query()
        if filters.category_id is not None:
            query = query.where(PracticeModel.category_id == filters.category_id)
        if filters.difficulty is not None:
            query = query.where(PracticeModel.difficulty == filters.difficulty)
        if filters.type is not None:
            query = query.where(PracticeModel.type == filters.type)
        if filters.status is not None:
            query = query.where(PracticeModel.status == filters.status)
        if filters.technology is not None:
            query = query.where(PracticeModel.technologies.any(filters.technology))
        if filters.has_ai is not None:
            if filters.has_ai:
                query = query.where(PracticeModel.ai_configuration != {})
            else:
                query = query.where(PracticeModel.ai_configuration == {})
        if filters.search:
            like = f"%{filters.search.lower()}%"
            query = query.where(func.lower(PracticeModel.title).like(like))

        total = self._session.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = self._session.scalars(
            query.order_by(PracticeModel.created_at.desc())
            .offset(page_request.offset)
            .limit(page_request.page_size)
        )
        return Page(
            items=[_practice_to_domain(m) for m in rows],
            total=total,
            page=page_request.page,
            page_size=page_request.page_size,
        )


class SqlAlchemyPracticeCategoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, category_id: uuid.UUID) -> PracticeCategory | None:
        model = self._session.get(PracticeCategoryModel, category_id)
        return _category_to_domain(model) if model else None

    def get_by_slug(self, slug: str) -> PracticeCategory | None:
        model = self._session.scalar(
            select(PracticeCategoryModel).where(PracticeCategoryModel.slug == slug)
        )
        return _category_to_domain(model) if model else None

    def list_all(self) -> list[PracticeCategory]:
        rows = self._session.scalars(
            select(PracticeCategoryModel).order_by(PracticeCategoryModel.name)
        )
        return [_category_to_domain(m) for m in rows]

    def add(self, category: PracticeCategory) -> PracticeCategory:
        model = PracticeCategoryModel(
            name=category.name,
            slug=category.slug,
            description=category.description,
            parent_id=category.parent_id,
        )
        self._session.add(model)
        self._session.flush()
        return _category_to_domain(model)


class SqlAlchemyPracticeTagRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_slug(self, slug: str) -> PracticeTag | None:
        model = self._session.scalar(select(PracticeTagModel).where(PracticeTagModel.slug == slug))
        return _tag_to_domain(model) if model else None

    def list_all(self) -> list[PracticeTag]:
        rows = self._session.scalars(select(PracticeTagModel).order_by(PracticeTagModel.name))
        return [_tag_to_domain(m) for m in rows]

    def get_or_create(self, name: str, slug: str) -> PracticeTag:
        model = self._session.scalar(select(PracticeTagModel).where(PracticeTagModel.slug == slug))
        if model is None:
            model = PracticeTagModel(name=name, slug=slug)
            self._session.add(model)
            self._session.flush()
        return _tag_to_domain(model)


def _narration_to_domain(model: PracticeNarrationModel) -> PracticeNarration:
    return PracticeNarration(
        id=model.id,
        practice_id=model.practice_id,
        lang=model.lang,
        storage_key=model.storage_key,
        text_hash=model.text_hash,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyPracticeNarrationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_practice_and_lang(
        self, practice_id: uuid.UUID, lang: str
    ) -> PracticeNarration | None:
        model = self._session.scalar(
            select(PracticeNarrationModel).where(
                PracticeNarrationModel.practice_id == practice_id,
                PracticeNarrationModel.lang == lang,
            )
        )
        return _narration_to_domain(model) if model else None

    def upsert(self, narration: PracticeNarration) -> PracticeNarration:
        model = self._session.scalar(
            select(PracticeNarrationModel).where(
                PracticeNarrationModel.practice_id == narration.practice_id,
                PracticeNarrationModel.lang == narration.lang,
            )
        )
        if model is None:
            model = PracticeNarrationModel(
                practice_id=narration.practice_id,
                lang=narration.lang,
                storage_key=narration.storage_key,
                text_hash=narration.text_hash,
            )
            self._session.add(model)
        else:
            model.storage_key = narration.storage_key
            model.text_hash = narration.text_hash
        self._session.flush()
        return _narration_to_domain(model)
