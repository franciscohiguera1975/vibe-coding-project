import uuid

from fastapi import APIRouter, Depends

from app.application.dto.user_dto import CreateUserInput
from app.application.use_cases.users.assign_role import AssignRoleUseCase
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.interfaces.http.controllers.auth_controller import user_to_public
from app.interfaces.http.dependencies.auth import require_permission
from app.interfaces.http.dependencies.use_cases import (
    get_assign_role_use_case,
    get_create_user_use_case,
)
from app.interfaces.http.schemas.auth import UserPublic
from app.interfaces.http.schemas.user import AssignRoleRequest, CreateUserRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserPublic, status_code=201)
def create_user(
    payload: CreateUserRequest,
    actor: User = Depends(require_permission(perm.USER_CREATE)),
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserPublic:
    user = use_case.execute(
        actor=actor,
        data=CreateUserInput(
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            role_names=payload.role_names,
        ),
    )
    return user_to_public(user)


@router.post("/{user_id}/roles", response_model=UserPublic)
def assign_role(
    user_id: uuid.UUID,
    payload: AssignRoleRequest,
    actor: User = Depends(require_permission(perm.USER_UPDATE)),
    use_case: AssignRoleUseCase = Depends(get_assign_role_use_case),
) -> UserPublic:
    user = use_case.execute(actor=actor, user_id=user_id, role_name=payload.role_name)
    return user_to_public(user)
