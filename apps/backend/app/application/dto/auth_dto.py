from dataclasses import dataclass

from app.domain.entities.identity import User


@dataclass(frozen=True, slots=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    user: User
    token_type: str = "bearer"
