from collections.abc import Callable

from fastapi import Depends

from app.application.ports.ai_provider import AIProvider
from app.application.ports.storage import StoragePort
from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.images.analyze_image import AnalyzeImageUseCase
from app.application.use_cases.images.process_image import ProcessImageUseCase
from app.infrastructure.config import Settings, get_settings
from app.interfaces.http.dependencies.ai import get_ai_provider
from app.interfaces.http.dependencies.storage import get_storage_port
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory


def get_process_image_use_case(
    storage_port: StoragePort = Depends(get_storage_port),
    settings: Settings = Depends(get_settings),
) -> ProcessImageUseCase:
    return ProcessImageUseCase(storage_port, settings.storage_max_upload_mb)


def get_analyze_image_use_case(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
    ai_provider: AIProvider = Depends(get_ai_provider),
) -> AnalyzeImageUseCase:
    return AnalyzeImageUseCase(uow_factory, ai_provider)
