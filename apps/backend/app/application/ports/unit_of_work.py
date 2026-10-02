from typing import Protocol

from app.domain.repositories.identity_repository import (
    PermissionRepository,
    RoleRepository,
    UserRepository,
)
from app.domain.repositories.practice_repository import (
    PracticeCategoryRepository,
    PracticeRepository,
    PracticeTagRepository,
)


class UnitOfWork(Protocol):
    """Limite transaccional explicito (recomendado en la validacion de arquitectura):
    los casos de uso que tocan varios repositorios lo hacen dentro de un `with uow:`,
    y el commit/rollback ocurre aqui, no dentro de cada repositorio."""

    users: UserRepository
    roles: RoleRepository
    permissions: PermissionRepository
    practices: PracticeRepository
    practice_categories: PracticeCategoryRepository
    practice_tags: PracticeTagRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
