import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin, utcnow


class ConfigurationModel(TimestampMixin, Base):
    __tablename__ = "configurations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    value: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    audit_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
