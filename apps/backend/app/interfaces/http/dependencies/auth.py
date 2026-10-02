import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.ports.security import TokenError, TokenService
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import User
from app.interfaces.http.dependencies.security import get_token_service
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory

_bearer_scheme = HTTPBearer(auto_error=True)
_optional_bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_user(
    token: str, token_service: TokenService, uow_factory: Callable[[], UnitOfWork]
) -> User | None:
    try:
        claims = token_service.decode(token)
    except TokenError:
        return None
    if claims.get("type") != "access":
        return None
    try:
        user_id = uuid.UUID(claims["sub"])
    except (KeyError, ValueError):
        return None

    with uow_factory() as uow:
        user = uow.users.get_by_id(user_id)
    return user if (user is not None and user.is_active) else None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    token_service: TokenService = Depends(get_token_service),
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> User:
    """Decodifica el access token y recupera al usuario con sus roles/permisos
    actuales (no confia en los claims del token para autorizar, solo para identificar)."""
    user = _resolve_user(credentials.credentials, token_service, uow_factory)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido o expirado"
        )
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer_scheme),
    token_service: TokenService = Depends(get_token_service),
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> User | None:
    """Para endpoints publicos que personalizan la respuesta si hay sesion (p.ej. el
    catalogo mostrando borradores a quien tiene practice:read), sin exigir login."""
    if credentials is None:
        return None
    return _resolve_user(credentials.credentials, token_service, uow_factory)


def require_permission(permission_code: str) -> Callable[..., User]:
    """Dependencia de RBAC (§15/§27): `Depends(require_permission("practice:create"))`."""

    def _check(user: User = Depends(get_current_user)) -> User:
        if not user.has_permission(permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permission_code}",
            )
        return user

    return _check
