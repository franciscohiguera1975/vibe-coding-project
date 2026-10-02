import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.application.ports.security import TokenError
from app.infrastructure.config import Settings


class JoseTokenService:
    """Implementa application.ports.security.TokenService con JWT (python-jose)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _create_token(
        self,
        *,
        subject: str,
        expires_in_seconds: int,
        token_type: str,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": subject,
            "type": token_type,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + timedelta(seconds=expires_in_seconds),
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(
            payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm
        )

    def create_access_token(
        self, *, subject: str, extra_claims: dict[str, Any] | None = None
    ) -> str:
        return self._create_token(
            subject=subject,
            expires_in_seconds=self._settings.jwt_access_expires_seconds,
            token_type="access",
            extra_claims=extra_claims,
        )

    def create_refresh_token(self, *, subject: str) -> str:
        return self._create_token(
            subject=subject,
            expires_in_seconds=self._settings.jwt_refresh_expires_seconds,
            token_type="refresh",
        )

    def decode(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token, self._settings.jwt_secret, algorithms=[self._settings.jwt_algorithm]
            )
        except JWTError as exc:
            raise TokenError(str(exc)) from exc
