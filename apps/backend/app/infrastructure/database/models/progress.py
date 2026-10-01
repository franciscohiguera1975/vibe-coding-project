import enum
import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EVALUATED = "evaluated"
    ABANDONED = "abandoned"


class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class EvaluatorType(str, enum.Enum):
    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"


class StudentPracticeAttemptModel(TimestampMixin, Base):
    __tablename__ = "student_practice_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    practice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[AttemptStatus] = mapped_column(
        SAEnum(AttemptStatus, name="attempt_status"),
        default=AttemptStatus.IN_PROGRESS,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class PracticeSubmissionModel(TimestampMixin, Base):
    __tablename__ = "practice_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_practice_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    practice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practices.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(nullable=False)


class PracticeEvaluationModel(TimestampMixin, Base):
    """Resultado de evaluar un envio (EvaluatePractice), no la configuracion de evaluacion
    (esa vive en practices.evaluation)."""

    __tablename__ = "practice_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("practice_submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    passed: Mapped[bool] = mapped_column(nullable=False)
    feedback: Mapped[str] = mapped_column(String(2000), default="", nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    evaluated_by: Mapped[EvaluatorType] = mapped_column(
        SAEnum(EvaluatorType, name="evaluator_type"), nullable=False
    )
    evaluator_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class StudentProgressModel(TimestampMixin, Base):
    __tablename__ = "student_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "practice_id", name="uq_student_progress_user_practice"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    practice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("practices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ProgressStatus] = mapped_column(
        SAEnum(ProgressStatus, name="progress_status"),
        default=ProgressStatus.NOT_STARTED,
        nullable=False,
    )
    best_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    attempts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_attempt_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
