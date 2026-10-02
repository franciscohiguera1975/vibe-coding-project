import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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


@dataclass(slots=True)
class StudentPracticeAttempt:
    user_id: uuid.UUID
    practice_id: uuid.UUID
    attempt_number: int
    started_at: datetime
    id: uuid.UUID | None = None
    status: AttemptStatus = AttemptStatus.IN_PROGRESS
    finished_at: datetime | None = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PracticeSubmission:
    attempt_id: uuid.UUID
    practice_id: uuid.UUID
    user_id: uuid.UUID
    payload: dict[str, Any]
    submitted_at: datetime
    id: uuid.UUID | None = None


@dataclass(slots=True)
class PracticeEvaluation:
    submission_id: uuid.UUID
    score: float
    passed: bool
    evaluated_by: EvaluatorType
    id: uuid.UUID | None = None
    feedback: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    evaluator_user_id: uuid.UUID | None = None


@dataclass(slots=True)
class StudentProgress:
    user_id: uuid.UUID
    practice_id: uuid.UUID
    id: uuid.UUID | None = None
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    best_score: float | None = None
    attempts_count: int = 0
    last_attempt_at: datetime | None = None
    completed_at: datetime | None = None
