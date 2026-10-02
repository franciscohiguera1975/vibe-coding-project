from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.system import AuditLog
from app.domain.exceptions import PermissionDeniedError
from app.domain.value_objects.pagination import Page, PageRequest


class ListAuditLogsUseCase:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, page_request: PageRequest) -> Page[AuditLog]:
        if not actor.has_permission(perm.AUDIT_READ):
            raise PermissionDeniedError(perm.AUDIT_READ)

        with self._uow_factory() as uow:
            return uow.audit_logs.list(page_request)
