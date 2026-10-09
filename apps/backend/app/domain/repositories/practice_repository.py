import uuid
from dataclasses import dataclass
from typing import Protocol

from app.domain.entities.practice import (
    Practice,
    PracticeCategory,
    PracticeDifficulty,
    PracticeNarration,
    PracticeStatus,
    PracticeTag,
)
from app.domain.value_objects.pagination import Page, PageRequest


@dataclass(frozen=True, slots=True)
class PracticeFilters:
    """Filtros de catalogo (Prompt Maestro §14): categoria, nivel, tecnologia, tipo, IA/imagenes."""

    category_id: uuid.UUID | None = None
    difficulty: PracticeDifficulty | None = None
    technology: str | None = None
    type: str | None = None
    status: PracticeStatus | None = None
    has_ai: bool | None = None
    search: str | None = None


class PracticeRepository(Protocol):
    def get_by_id(self, practice_id: uuid.UUID) -> Practice | None: ...

    def get_by_slug(self, slug: str) -> Practice | None: ...

    def add(self, practice: Practice) -> Practice: ...

    def update(self, practice: Practice) -> Practice: ...

    def delete(self, practice_id: uuid.UUID) -> None: ...

    def list(self, filters: PracticeFilters, page_request: PageRequest) -> Page[Practice]: ...


class PracticeCategoryRepository(Protocol):
    def get_by_id(self, category_id: uuid.UUID) -> PracticeCategory | None: ...

    def get_by_slug(self, slug: str) -> PracticeCategory | None: ...

    def list_all(self) -> list[PracticeCategory]: ...

    def add(self, category: PracticeCategory) -> PracticeCategory: ...


class PracticeTagRepository(Protocol):
    def get_by_slug(self, slug: str) -> PracticeTag | None: ...

    def list_all(self) -> list[PracticeTag]: ...

    def get_or_create(self, name: str, slug: str) -> PracticeTag: ...


class PracticeNarrationRepository(Protocol):
    def get_by_practice_and_lang(
        self, practice_id: uuid.UUID, lang: str
    ) -> PracticeNarration | None: ...

    def upsert(self, narration: PracticeNarration) -> PracticeNarration: ...
