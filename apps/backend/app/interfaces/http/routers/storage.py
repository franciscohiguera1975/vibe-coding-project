import mimetypes

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.application.ports.storage import StoragePort
from app.infrastructure.storage.local_adapter import LocalStorageAdapter
from app.interfaces.http.dependencies.storage import get_storage_port

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/{key}")
def get_stored_file(key: str, storage_port: StoragePort = Depends(get_storage_port)) -> Response:
    """Sirve un archivo guardado por LocalStorageAdapter. Con MinIO/S3 `get_url`
    devuelve un enlace directo al proveedor y este endpoint no se usa."""
    if not isinstance(storage_port, LocalStorageAdapter):
        raise NotImplementedError("Este proveedor de almacenamiento sirve archivos directamente")
    content = storage_port.read(key)
    media_type = mimetypes.guess_type(key)[0] or "application/octet-stream"
    return Response(content=content, media_type=media_type)
