from collections.abc import Callable

from fastapi import APIRouter, Depends

from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.roles.assign_permission import AssignPermissionUseCase
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.interfaces.http.controllers.role_controller import role_to_public
from app.interfaces.http.dependencies.auth import require_permission
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory
from app.interfaces.http.dependencies.use_cases import get_assign_permission_use_case
from app.interfaces.http.schemas.role import AssignPermissionRequest, RolePublic

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RolePublic])
def list_roles(
    actor: User = Depends(require_permission(perm.USER_READ)),
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> list[RolePublic]:
    with uow_factory() as uow:
        roles = uow.roles.list_all()
    return [role_to_public(r) for r in roles]


@router.post("/{role_name}/permissions", response_model=RolePublic)
def assign_permission(
    role_name: str,
    payload: AssignPermissionRequest,
    actor: User = Depends(require_permission(perm.ROLE_ASSIGN_PERMISSION)),
    use_case: AssignPermissionUseCase = Depends(get_assign_permission_use_case),
) -> RolePublic:
    role = use_case.execute(
        actor=actor, role_name=role_name, permission_code=payload.permission_code
    )
    return role_to_public(role)
