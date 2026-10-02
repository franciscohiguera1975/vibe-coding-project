from collections.abc import Callable

from app.application.dto.auth_dto import AuthTokens
from app.application.ports.security import PasswordHasher, TokenService
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import InvalidCredentialsError


class LoginUseCase:
    """Autentica con email/password y emite un par access/refresh JWT (Prompt Maestro §27)."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, *, email: str, password: str) -> AuthTokens:
        with self._uow_factory() as uow:
            user = uow.users.get_by_email(email.strip().lower())

        if user is None or not user.is_active:
            raise InvalidCredentialsError()
        if not self._password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError()

        role_names = [r.name for r in user.roles]
        access_token = self._token_service.create_access_token(
            subject=str(user.id), extra_claims={"roles": role_names}
        )
        refresh_token = self._token_service.create_refresh_token(subject=str(user.id))
        return AuthTokens(access_token=access_token, refresh_token=refresh_token, user=user)
