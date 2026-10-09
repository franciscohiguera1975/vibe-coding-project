from collections.abc import Callable

from fastapi import Depends

from app.application.ports.notifications import EmailSender
from app.application.ports.security import PasswordHasher, TokenService
from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.request_password_reset import RequestPasswordResetUseCase
from app.application.use_cases.auth.reset_password import ResetPasswordUseCase
from app.application.use_cases.roles.assign_permission import AssignPermissionUseCase
from app.application.use_cases.users.assign_role import AssignRoleUseCase
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.infrastructure.config import Settings, get_settings
from app.interfaces.http.dependencies.email import get_email_sender
from app.interfaces.http.dependencies.security import get_password_hasher, get_token_service
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory


def get_login_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: TokenService = Depends(get_token_service),
) -> LoginUseCase:
    return LoginUseCase(uow_factory, password_hasher, token_service)


def get_refresh_token_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    token_service: TokenService = Depends(get_token_service),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(uow_factory, token_service)


def get_request_password_reset_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    email_sender: EmailSender = Depends(get_email_sender),
    settings: Settings = Depends(get_settings),
) -> RequestPasswordResetUseCase:
    return RequestPasswordResetUseCase(uow_factory, email_sender, settings)


def get_reset_password_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(uow_factory, password_hasher)


def get_create_user_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> CreateUserUseCase:
    return CreateUserUseCase(uow_factory, password_hasher)


def get_assign_role_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> AssignRoleUseCase:
    return AssignRoleUseCase(uow_factory)


def get_assign_permission_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> AssignPermissionUseCase:
    return AssignPermissionUseCase(uow_factory)
