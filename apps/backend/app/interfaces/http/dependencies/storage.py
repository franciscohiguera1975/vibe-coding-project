from functools import lru_cache

from app.application.ports.storage import StoragePort
from app.infrastructure.config import get_settings
from app.infrastructure.storage.local_adapter import LocalStorageAdapter


@lru_cache
def get_storage_port() -> StoragePort:
    """Selecciona el adaptador segun STORAGE_PROVIDER (Prompt Maestro §20). local es
    el default y el unico operativo sin credenciales adicionales."""
    settings = get_settings()
    if settings.storage_provider == "minio":
        from app.infrastructure.storage.minio_adapter import MinIOAdapter

        return MinIOAdapter(
            endpoint=settings.storage_minio_endpoint,
            access_key=settings.storage_minio_access_key,
            secret_key=settings.storage_minio_secret_key,
            bucket=settings.storage_minio_bucket,
        )
    if settings.storage_provider == "s3":
        from app.infrastructure.storage.s3_adapter import S3Adapter

        return S3Adapter(bucket=settings.storage_s3_bucket)
    return LocalStorageAdapter(settings.storage_local_path, settings.backend_url)
