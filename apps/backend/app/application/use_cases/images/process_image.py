from dataclasses import dataclass

from app.application.ports.storage import StoragePort
from app.infrastructure.storage.file_validation import validate_image_file


@dataclass(frozen=True, slots=True)
class ProcessImageResult:
    key: str
    url: str


class ProcessImageUseCase:
    """ProcessImage (Prompt Maestro §8, §20): valida y almacena un archivo de imagen,
    independiente del proveedor de almacenamiento configurado."""

    def __init__(self, storage_port: StoragePort, max_size_mb: int) -> None:
        self._storage_port = storage_port
        self._max_size_mb = max_size_mb

    def execute(self, *, filename: str, content_type: str, file_bytes: bytes) -> ProcessImageResult:
        validate_image_file(
            filename=filename,
            content_type=content_type,
            file_bytes=file_bytes,
            max_size_mb=self._max_size_mb,
        )
        key = self._storage_port.upload(file_bytes, filename=filename, content_type=content_type)
        return ProcessImageResult(key=key, url=self._storage_port.get_url(key))
