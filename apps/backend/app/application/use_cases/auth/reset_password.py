import hashlib
from collections.abc import Callable
from datetime import UTC, datetime

from app.application.ports.security import PasswordHasher
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import InvalidOrExpiredTokenError


class ResetPasswordUseCase:
    """Confirma el restablecimiento: valida el token de un solo uso (Prompt Maestro
    §27, mismo hasher bcrypt que login) y fija la nueva contraseña."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        password_hasher: PasswordHasher,
    ) -> None:
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher

    def execute(self, *, token: str, new_password: str) -> None:
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        with self._uow_factory() as uow:
            reset_token = uow.password_reset_tokens.get_by_token_hash(token_hash)
            now = datetime.now(UTC).replace(tzinfo=None)
            if reset_token is None or not reset_token.is_valid(now=now):
                raise InvalidOrExpiredTokenError()

            user = uow.users.get_by_id(reset_token.user_id)
            if user is None or not user.is_active:
                raise InvalidOrExpiredTokenError()

            user.password_hash = self._password_hasher.hash(new_password)
            uow.users.update(user)
            uow.password_reset_tokens.mark_used(reset_token.id)
            uow.commit()
