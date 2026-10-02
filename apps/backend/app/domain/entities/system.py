import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Configuration:
    key: str
    value: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    id: uuid.UUID | None = None


@dataclass(slots=True)
class AuditLog:
    action: str
    entity_type: str
    created_at: datetime
    id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    entity_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    ip_address: str | None = None
