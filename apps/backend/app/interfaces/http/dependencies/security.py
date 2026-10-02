from functools import lru_cache

from app.application.ports.security import PasswordHasher, TokenService
from app.infrastructure.config import get_settings
from app.infrastructure.security.password_hasher import BcryptPasswordHasher
from app.infrastructure.security.token_service import JoseTokenService


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


@lru_cache
def get_token_service() -> TokenService:
    return JoseTokenService(get_settings())
