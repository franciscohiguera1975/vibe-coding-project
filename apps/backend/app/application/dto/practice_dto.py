from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CreatePracticeInput:
    title: str
    type: str
    slug: str | None = None
    description: str = ""
    objectives: list[str] = field(default_factory=list)
    instructions: str = ""
    category_slug: str | None = None
    difficulty: str = "beginner"
    estimated_time_minutes: int = 30
    technologies: list[str] = field(default_factory=list)
    tag_names: list[str] = field(default_factory=list)
    content: dict[str, Any] = field(default_factory=dict)
    evaluation: dict[str, Any] = field(default_factory=dict)
    ai_configuration: dict[str, Any] = field(default_factory=dict)
    embedding_configuration: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class UpdatePracticeInput:
    title: str | None = None
    description: str | None = None
    objectives: list[str] | None = None
    instructions: str | None = None
    category_slug: str | None = None
    difficulty: str | None = None
    estimated_time_minutes: int | None = None
    technologies: list[str] | None = None
    tag_names: list[str] | None = None
    content: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    ai_configuration: dict[str, Any] | None = None
    embedding_configuration: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
