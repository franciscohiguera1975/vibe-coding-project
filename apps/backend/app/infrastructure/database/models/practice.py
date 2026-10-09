import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin
from app.infrastructure.database.models.catalog import practice_practice_tags

if TYPE_CHECKING:
    from app.infrastructure.database.models.catalog import (
        PracticeCategoryModel,
        PracticeTagModel,
    )


class PracticeDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PracticeStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PracticeModel(TimestampMixin, Base):
    """Entidad reutilizable de practica (Prompt Maestro §16). `type` + `content` son
    data-driven: una practica nueva de un tipo existente no requiere cambios de codigo."""

    __tablename__ = "practices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    objectives: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, default="", nullable=False)

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practice_categories.id", ondelete="SET NULL"), nullable=True
    )
    difficulty: Mapped[PracticeDifficulty] = mapped_column(
        SAEnum(PracticeDifficulty, name="practice_difficulty"),
        default=PracticeDifficulty.BEGINNER,
        nullable=False,
    )
    estimated_time_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    technologies: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    # Tipo de practica: "software" | "image" | ... (string libre y extensible, ver registry
    # de tipos en el frontend — agregar un tipo nuevo no debe forzar una migracion).
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    content: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    evaluation: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ai_configuration: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    embedding_configuration: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    status: Mapped[PracticeStatus] = mapped_column(
        SAEnum(PracticeStatus, name="practice_status"), default=PracticeStatus.DRAFT, nullable=False
    )
    practice_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Traducciones opcionales del contenido pedagogico por idioma, p.ej.
    # {"en": {"title": ..., "description": ..., "objectives": [...], "instructions": ...,
    # "content": {...overlay parcial...}}, "pt": {...}}. Solo se incluyen las claves que
    # difieren del espanol base (ver app.domain.services.practice_localization).
    translations: Mapped[dict] = mapped_column(
        JSONB, default=dict, server_default="{}", nullable=False
    )

    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    category: Mapped["PracticeCategoryModel | None"] = relationship(back_populates="practices")
    tags: Mapped[list["PracticeTagModel"]] = relationship(
        secondary=practice_practice_tags, back_populates="practices"
    )
    contents: Mapped[list["PracticeContentModel"]] = relationship(
        back_populates="practice", cascade="all, delete-orphan"
    )


class PracticeContentModel(TimestampMixin, Base):
    """Historial versionado del contenido de una practica (practice_contents)."""

    __tablename__ = "practice_contents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practices.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    practice: Mapped["PracticeModel"] = relationship(back_populates="contents")


class PracticeNarrationModel(TimestampMixin, Base):
    """Audio narrado (TTS) de una practica por idioma (practice_narrations). Un unico
    registro por (practice_id, lang): se sobrescribe cuando el texto fuente cambia
    (ver app.domain.entities.practice.PracticeNarration y GeneratePracticeNarrationUseCase)."""

    __tablename__ = "practice_narrations"
    __table_args__ = (
        UniqueConstraint("practice_id", "lang", name="uq_practice_narrations_practice_lang"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practices.id", ondelete="CASCADE"), nullable=False
    )
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
