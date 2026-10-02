from datetime import UTC, datetime
from typing import Any

from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.domain.entities.system import AuditLog


def record(
    uow: UnitOfWork,
    *,
    actor: User,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Escribe una entrada de auditoria dentro de la misma transaccion del caso de uso
    (Prompt Maestro §27). Se llama explicitamente desde las acciones administrativas
    sensibles, no via un decorador generico (mantiene la trazabilidad explicita)."""
    uow.audit_logs.add(
        AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=actor.id,
            metadata=metadata or {},
            created_at=datetime.now(UTC),
        )
    )
