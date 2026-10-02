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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    token_service: TokenService = Depends(get_token_service),
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> User:
    """Decodifica el access token y recupera al usuario con sus roles/permisos
    actuales (no confia en los claims del token para autorizar, solo para identificar)."""
    try:
        claims = token_service.decode(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido o expirado"
        ) from exc

    if claims.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    try:
        user_id = uuid.UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido"
        ) from exc

    with uow_factory() as uow:
        user = uow.users.get_by_id(user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    return user


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
