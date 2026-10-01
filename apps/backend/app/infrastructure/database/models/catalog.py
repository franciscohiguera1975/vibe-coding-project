import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    # Solo para chequeo de tipos: evita import circular en tiempo de ejecucion
    # (practice.py ya importa este modulo para la tabla de asociacion).
    from app.infrastructure.database.models.practice import PracticeModel

practice_practice_tags = Table(
    "practice_practice_tags",
    Base.metadata,
    Column(
        "practice_id",
        UUID(as_uuid=True),
        ForeignKey("practices.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        UUID(as_uuid=True),
        ForeignKey("practice_tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class PracticeCategoryModel(TimestampMixin, Base):
    __tablename__ = "practice_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practice_categories.id", ondelete="SET NULL"), nullable=True
    )

    practices: Mapped[list["PracticeModel"]] = relationship(back_populates="category")


class PracticeTagModel(TimestampMixin, Base):
    __tablename__ = "practice_tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    practices: Mapped[list["PracticeModel"]] = relationship(
        secondary=practice_practice_tags, back_populates="tags"
    )
