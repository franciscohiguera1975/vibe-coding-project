import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


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


@dataclass(slots=True)
class AISession:
    user_id: uuid.UUID
    started_at: datetime
    id: uuid.UUID | None = None
    practice_id: uuid.UUID | None = None
    agent_type: str = "tutor"
    status: AISessionStatus = AISessionStatus.ACTIVE
    ended_at: datetime | None = None
    iterations_used: int = 0
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AIMessage:
    session_id: uuid.UUID
    role: AIMessageRole
    content: str
    sequence: int
    id: uuid.UUID | None = None


@dataclass(slots=True)
class AIToolCall:
    session_id: uuid.UUID
    iteration_index: int
    tool_name: str
    status: AIToolCallStatus
    id: uuid.UUID | None = None
    arguments: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
