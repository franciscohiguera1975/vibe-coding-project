"""LocalStorageAdapter (Prompt Maestro §20): implementacion por defecto de
StoragePort, guarda archivos en disco bajo STORAGE_LOCAL_PATH. Las claves
incluyen un UUID para evitar colisiones y no exponer el nombre original."""

import uuid
from pathlib import Path

from app.domain.exceptions import NotFoundError


class LocalStorageAdapter:
    def __init__(self, base_path: str, backend_url: str) -> None:
        self._base_path = Path(base_path)
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._backend_url = backend_url.rstrip("/")

    def upload(self, file_bytes: bytes, *, filename: str, content_type: str) -> str:
        extension = Path(filename).suffix.lower()
        key = f"{uuid.uuid4().hex}{extension}"
        (self._base_path / key).write_bytes(file_bytes)
        return key

    def delete(self, key: str) -> None:
        path = self._safe_path(key)
        path.unlink(missing_ok=True)

    def get_url(self, key: str) -> str:
        return f"{self._backend_url}/api/storage/{key}"

    def read(self, key: str) -> bytes:
        path = self._safe_path(key)
        if not path.exists():
            raise NotFoundError("StoredFile", key)
        return path.read_bytes()

    def _safe_path(self, key: str) -> Path:
        # Evita path traversal: el key nunca debe salir de base_path.
        path = (self._base_path / key).resolve()
        if self._base_path.resolve() not in path.parents and path != self._base_path.resolve():
            raise NotFoundError("StoredFile", key)
        return path
