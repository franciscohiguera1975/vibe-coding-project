from collections.abc import Callable

from app.application.dto.user_dto import CreateUserInput
from app.application.ports.security import PasswordHasher
from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.domain.value_objects.email import Email


class CreateUserUseCase:
    """CreateUser (Prompt Maestro §8): solo un actor con user:create puede crear usuarios
    (no hay auto-registro publico en esta plataforma, ver §14/§15)."""

    def __init__(
        self, uow_factory: Callable[[], UnitOfWork], password_hasher: PasswordHasher
    ) -> None:
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher

    def execute(self, *, actor: User, data: CreateUserInput) -> User:
        if not actor.has_permission(perm.USER_CREATE):
            raise PermissionDeniedError(perm.USER_CREATE)

        email = str(Email(data.email))
        password_hash = self._password_hasher.hash(data.password)

        with self._uow_factory() as uow:
            if uow.users.get_by_email(email) is not None:
                raise ConflictError(f"Ya existe un usuario con el email {email!r}")

            roles = []
            for role_name in data.role_names:
                role = uow.roles.get_by_name(role_name)
                if role is None:
                    raise NotFoundError("Role", role_name)
                roles.append(role)

            new_user = User(
                email=email,
                password_hash=password_hash,
                full_name=data.full_name,
                roles=roles,
            )
            created = uow.users.add(new_user)
            uow.commit()
            return created
