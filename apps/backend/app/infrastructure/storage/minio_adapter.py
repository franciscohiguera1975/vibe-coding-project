"""MinIOAdapter (Prompt Maestro §20): interfaz completa de StoragePort para MinIO.
No operativo en este entregable (requiere el SDK de MinIO y credenciales reales);
documentado como evolucion futura en docs/architecture.md. Implementarlo consiste
en reemplazar los cuerpos de estos metodos con llamadas al cliente `minio.Minio`
manteniendo la misma firma, sin tocar los casos de uso que dependen de StoragePort."""


class MinIOAdapter:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str) -> None:
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket

    def upload(self, file_bytes: bytes, *, filename: str, content_type: str) -> str:
        raise NotImplementedError(
            "MinIOAdapter aun no esta implementado; configure STORAGE_PROVIDER=local "
            "o implemente este adaptador con el SDK de MinIO (ver docs/architecture.md)."
        )

    def delete(self, key: str) -> None:
        raise NotImplementedError("MinIOAdapter aun no esta implementado")

    def get_url(self, key: str) -> str:
        raise NotImplementedError("MinIOAdapter aun no esta implementado")
