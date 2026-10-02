import uuid
from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.exceptions import NotFoundError, PermissionDeniedError


class AssignRoleUseCase:
    """AssignRole (Prompt Maestro §8)."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, user_id: uuid.UUID, role_name: str) -> User:
        if not actor.has_permission(perm.USER_UPDATE):
            raise PermissionDeniedError(perm.USER_UPDATE)

        with self._uow_factory() as uow:
            user = uow.users.get_by_id(user_id)
            if user is None:
                raise NotFoundError("User", str(user_id))

            role = uow.roles.get_by_name(role_name)
            if role is None:
                raise NotFoundError("Role", role_name)

            if not any(r.id == role.id for r in user.roles):
                user.roles.append(role)

            updated = uow.users.update(user)
            uow.commit()
            return updated
