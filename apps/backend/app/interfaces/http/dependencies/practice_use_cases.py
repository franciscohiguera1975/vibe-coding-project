from collections.abc import Callable

from fastapi import Depends

from app.application.ports.evaluation import EvaluationPort
from app.application.ports.narration import NarrationPort
from app.application.ports.storage import StoragePort
from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.practices.create_practice import CreatePracticeUseCase
from app.application.use_cases.practices.evaluate_practice import EvaluatePracticeUseCase
from app.application.use_cases.practices.generate_practice_narration import (
    GeneratePracticeNarrationUseCase,
)
from app.application.use_cases.practices.get_practice import GetPracticeUseCase
from app.application.use_cases.practices.get_practice_narration import (
    GetPracticeNarrationUseCase,
)
from app.application.use_cases.practices.list_practices import ListPracticesUseCase
from app.application.use_cases.practices.publish_practice import PublishPracticeUseCase
from app.application.use_cases.practices.start_practice import StartPracticeUseCase
from app.application.use_cases.practices.submit_practice import SubmitPracticeUseCase
from app.application.use_cases.practices.update_practice import UpdatePracticeUseCase
from app.interfaces.http.dependencies.evaluation import get_evaluation_port
from app.interfaces.http.dependencies.narration import get_narration_port
from app.interfaces.http.dependencies.storage import get_storage_port
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory


def get_create_practice_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> CreatePracticeUseCase:
    return CreatePracticeUseCase(uow_factory)


def get_update_practice_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> UpdatePracticeUseCase:
    return UpdatePracticeUseCase(uow_factory)


def get_publish_practice_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> PublishPracticeUseCase:
    return PublishPracticeUseCase(uow_factory)


def get_get_practice_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> GetPracticeUseCase:
    return GetPracticeUseCase(uow_factory)


def get_list_practices_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> ListPracticesUseCase:
    return ListPracticesUseCase(uow_factory)


def get_start_practice_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> StartPracticeUseCase:
    return StartPracticeUseCase(uow_factory)


def get_submit_practice_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> SubmitPracticeUseCase:
    return SubmitPracticeUseCase(uow_factory)


def get_evaluate_practice_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    evaluation_port: EvaluationPort = Depends(get_evaluation_port),
) -> EvaluatePracticeUseCase:
    return EvaluatePracticeUseCase(uow_factory, evaluation_port)


def get_generate_practice_narration_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    narration_port: NarrationPort = Depends(get_narration_port),
    storage_port: StoragePort = Depends(get_storage_port),
) -> GeneratePracticeNarrationUseCase:
    return GeneratePracticeNarrationUseCase(uow_factory, narration_port, storage_port)


def get_get_practice_narration_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> GetPracticeNarrationUseCase:
    return GetPracticeNarrationUseCase(uow_factory)
