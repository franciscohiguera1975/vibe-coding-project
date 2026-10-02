from collections.abc import Callable

from app.application.ports.unit_of_work import UnitOfWork
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


def get_uow_factory() -> Callable[[], UnitOfWork]:
    """Los casos de uso reciben esta factory e invocan `with uow_factory() as uow:` —
    el limite transaccional lo decide el caso de uso, no el router (Prompt Maestro §6)."""
    return SqlAlchemyUnitOfWork
