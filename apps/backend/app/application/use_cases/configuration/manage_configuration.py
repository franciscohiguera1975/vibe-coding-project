from collections.abc import Callable
from typing import Any

from app.application.ports.unit_of_work import UnitOfWork
from app.application.services import audit
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.system import Configuration
from app.domain.exceptions import PermissionDeniedError


class UpdateConfigurationUseCase:
    """ManageConfiguration (Prompt Maestro §8): crea o actualiza una configuracion por clave."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(
        self, *, actor: User, key: str, value: dict[str, Any], description: str = ""
    ) -> Configuration:
        if not actor.has_permission(perm.CONFIGURATION_UPDATE):
            raise PermissionDeniedError(perm.CONFIGURATION_UPDATE)

        with self._uow_factory() as uow:
            existing = uow.configurations.get_by_key(key)
            updated = uow.configurations.upsert(
                Configuration(
                    key=key,
                    value=value,
                    description=description or (existing.description if existing else ""),
                )
            )
            audit.record(
                uow,
                actor=actor,
                action="configuration.update",
                entity_type="Configuration",
                entity_id=key,
                metadata={"value": value},
            )
            uow.commit()
            return updated
