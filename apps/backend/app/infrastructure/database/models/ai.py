import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class AISessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    STOPPED = "stopped"


class AIMessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class AIToolCallStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"
    DENIED = "denied"


class AISessionModel(TimestampMixin, Base):
    """Sesion del AI Tutor Agent (Prompt Maestro §11). Independiente del almacenamiento
    de practicas: el agente tiene su propio repositorio (ver application/ports)."""

    __tablename__ = "ai_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    practice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practices.id", ondelete="SET NULL"), nullable=True
    )
    agent_type: Mapped[str] = mapped_column(String(50), default="tutor", nullable=False)
    status: Mapped[AISessionStatus] = mapped_column(
        SAEnum(AISessionStatus, name="ai_session_status"),
        default=AISessionStatus.ACTIVE,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    iterations_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    session_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class AIMessageModel(TimestampMixin, Base):
    __tablename__ = "ai_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[AIMessageRole] = mapped_column(
        SAEnum(AIMessageRole, name="ai_message_role"), nullable=False
    )
    content: Mapped[str] = mapped_column(String(8000), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)


class AIToolCallModel(TimestampMixin, Base):
    """Trazabilidad obligatoria de cada llamada a herramienta del agente (§11, §27)."""

    __tablename__ = "ai_tool_calls"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    iteration_index: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    arguments: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[AIToolCallStatus] = mapped_column(
        SAEnum(AIToolCallStatus, name="ai_tool_call_status"), nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
