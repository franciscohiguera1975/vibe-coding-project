from collections.abc import Callable

from fastapi import APIRouter, Depends

from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.configuration.manage_configuration import (
    UpdateConfigurationUseCase,
)
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.interfaces.http.controllers.system_controller import configuration_to_public
from app.interfaces.http.dependencies.admin_use_cases import get_update_configuration_use_case
from app.interfaces.http.dependencies.auth import require_permission
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory
from app.interfaces.http.schemas.configuration import (
    ConfigurationPublic,
    UpdateConfigurationRequest,
)

router = APIRouter(prefix="/configurations", tags=["configurations"])


@router.get("", response_model=list[ConfigurationPublic])
def list_configurations(
    actor: User = Depends(require_permission(perm.CONFIGURATION_READ)),
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> list[ConfigurationPublic]:
    with uow_factory() as uow:
        configurations = uow.configurations.list_all()
    return [configuration_to_public(c) for c in configurations]


@router.put("/{key}", response_model=ConfigurationPublic)
def update_configuration(
    key: str,
    payload: UpdateConfigurationRequest,
    actor: User = Depends(require_permission(perm.CONFIGURATION_UPDATE)),
    use_case: UpdateConfigurationUseCase = Depends(get_update_configuration_use_case),
) -> ConfigurationPublic:
    configuration = use_case.execute(
        actor=actor, key=key, value=payload.value, description=payload.description
    )
    return configuration_to_public(configuration)
