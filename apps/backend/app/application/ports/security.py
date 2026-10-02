from typing import Any, Protocol


class PasswordHasher(Protocol):
    def hash(self, plain_password: str) -> str: ...

    def verify(self, plain_password: str, password_hash: str) -> bool: ...


class TokenService(Protocol):
    """Emision/validacion de JWT (Prompt Maestro §27). `subject` es el id de usuario."""

    def create_access_token(
        self, *, subject: str, extra_claims: dict[str, Any] | None = None
    ) -> str: ...

    def create_refresh_token(self, *, subject: str) -> str: ...

    def decode(self, token: str) -> dict[str, Any]:
        """Lanza TokenError si el token es invalido o expiro."""
        ...


class TokenError(Exception):
    pass
