from typing import Protocol


class StoragePort(Protocol):
    """Puerto de almacenamiento de archivos (Prompt Maestro §20). Las practicas de
    imagenes no dependen del proveedor concreto (Local, MinIO, S3)."""

    def upload(self, file_bytes: bytes, *, filename: str, content_type: str) -> str:
        """Guarda el archivo y devuelve su clave/identificador de almacenamiento."""
        ...

    def delete(self, key: str) -> None: ...

    def get_url(self, key: str) -> str: ...
