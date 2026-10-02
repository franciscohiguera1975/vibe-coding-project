from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.application.services import audit
from app.domain import permissions as perm
from app.domain.entities.identity import Role, User
from app.domain.exceptions import NotFoundError, PermissionDeniedError


class AssignPermissionUseCase:
    """AssignPermission (Prompt Maestro §8): agrega un permiso a un rol."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, role_name: str, permission_code: str) -> Role:
        if not actor.has_permission(perm.ROLE_ASSIGN_PERMISSION):
            raise PermissionDeniedError(perm.ROLE_ASSIGN_PERMISSION)

        with self._uow_factory() as uow:
            role = uow.roles.get_by_name(role_name)
            if role is None:
                raise NotFoundError("Role", role_name)

            permission = uow.permissions.get_by_code(permission_code)
            if permission is None:
                raise NotFoundError("Permission", permission_code)

            if not any(p.id == permission.id for p in role.permissions):
                role.permissions.append(permission)

            updated = uow.roles.update(role)
            audit.record(
                uow,
                actor=actor,
                action="role.assign_permission",
                entity_type="Role",
                entity_id=str(role.id),
                metadata={"role_name": role_name, "permission_code": permission_code},
            )
            uow.commit()
            return updated
