import uuid
from collections.abc import Callable

from app.application.dto.auth_dto import AuthTokens
from app.application.ports.security import TokenError, TokenService
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.exceptions import InvalidCredentialsError


class RefreshTokenUseCase:
    """Intercambia un refresh token valido por un nuevo par access/refresh (rotacion)."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], token_service: TokenService) -> None:
        self._uow_factory = uow_factory
        self._token_service = token_service

    def execute(self, *, refresh_token: str) -> AuthTokens:
        try:
            claims = self._token_service.decode(refresh_token)
        except TokenError as exc:
            raise InvalidCredentialsError() from exc

        if claims.get("type") != "refresh":
            raise InvalidCredentialsError()

        try:
            user_id = uuid.UUID(claims["sub"])
        except (KeyError, ValueError) as exc:
            raise InvalidCredentialsError() from exc

        with self._uow_factory() as uow:
            user = uow.users.get_by_id(user_id)

        if user is None or not user.is_active:
            raise InvalidCredentialsError()

        role_names = [r.name for r in user.roles]
        access_token = self._token_service.create_access_token(
            subject=str(user.id), extra_claims={"roles": role_names}
        )
        new_refresh_token = self._token_service.create_refresh_token(subject=str(user.id))
        return AuthTokens(access_token=access_token, refresh_token=new_refresh_token, user=user)
