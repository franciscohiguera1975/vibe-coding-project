"""S3Adapter (Prompt Maestro §20): interfaz completa de StoragePort para Amazon S3
(o compatibles). No operativo en este entregable (requiere boto3 y credenciales
reales); documentado como evolucion futura en docs/architecture.md. Implementarlo
consiste en reemplazar los cuerpos de estos metodos con llamadas a `boto3.client("s3")`
manteniendo la misma firma, sin tocar los casos de uso que dependen de StoragePort."""


class S3Adapter:
    def __init__(self, bucket: str) -> None:
        self._bucket = bucket

    def upload(self, file_bytes: bytes, *, filename: str, content_type: str) -> str:
        raise NotImplementedError(
            "S3Adapter aun no esta implementado; configure STORAGE_PROVIDER=local o "
            "implemente este adaptador con boto3 (ver docs/architecture.md)."
        )

    def delete(self, key: str) -> None:
        raise NotImplementedError("S3Adapter aun no esta implementado")

    def get_url(self, key: str) -> str:
        raise NotImplementedError("S3Adapter aun no esta implementado")
