from collections.abc import Callable

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.audit.list_audit_logs import ListAuditLogsUseCase
from app.application.use_cases.catalog.manage_catalog import (
    CreatePracticeCategoryUseCase,
    CreatePracticeTagUseCase,
)
from app.application.use_cases.configuration.manage_configuration import (
    UpdateConfigurationUseCase,
)
from app.application.use_cases.users.list_users import ListUsersUseCase
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory


def get_list_users_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> ListUsersUseCase:
    return ListUsersUseCase(uow_factory)


def get_create_category_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> CreatePracticeCategoryUseCase:
    return CreatePracticeCategoryUseCase(uow_factory)


def get_create_tag_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> CreatePracticeTagUseCase:
    return CreatePracticeTagUseCase(uow_factory)


def get_update_configuration_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> UpdateConfigurationUseCase:
    return UpdateConfigurationUseCase(uow_factory)


def get_list_audit_logs_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> ListAuditLogsUseCase:
    return ListAuditLogsUseCase(uow_factory)
