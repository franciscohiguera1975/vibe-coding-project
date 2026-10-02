import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class PracticeDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PracticeStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass(slots=True)
class PracticeCategory:
    name: str
    slug: str
    description: str = ""
    id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None


@dataclass(slots=True)
class PracticeTag:
    name: str
    slug: str
    id: uuid.UUID | None = None


@dataclass(slots=True)
class Practice:
    """Entidad reutilizable de practica (Prompt Maestro §16). `content` es data-driven:
    agregar una practica nueva de un tipo existente no requiere cambios de codigo."""

    slug: str
    title: str
    type: str
    id: uuid.UUID | None = None
    description: str = ""
    objectives: list[str] = field(default_factory=list)
    instructions: str = ""
    category_id: uuid.UUID | None = None
    difficulty: PracticeDifficulty = PracticeDifficulty.BEGINNER
    estimated_time_minutes: int = 30
    technologies: list[str] = field(default_factory=list)
    tag_ids: list[uuid.UUID] = field(default_factory=list)
    content: dict[str, Any] = field(default_factory=dict)
    evaluation: dict[str, Any] = field(default_factory=dict)
    ai_configuration: dict[str, Any] = field(default_factory=dict)
    embedding_configuration: dict[str, Any] = field(default_factory=dict)
    status: PracticeStatus = PracticeStatus.DRAFT
    metadata: dict[str, Any] = field(default_factory=dict)
    created_by_id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_published(self) -> bool:
        return self.status == PracticeStatus.PUBLISHED
