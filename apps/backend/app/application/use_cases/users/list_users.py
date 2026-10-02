from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.exceptions import PermissionDeniedError
from app.domain.value_objects.pagination import Page, PageRequest


class ListUsersUseCase:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, *, actor: User, page_request: PageRequest) -> Page[User]:
        if not actor.has_permission(perm.USER_READ):
            raise PermissionDeniedError(perm.USER_READ)

        with self._uow_factory() as uow:
            return uow.users.list(page_request)
