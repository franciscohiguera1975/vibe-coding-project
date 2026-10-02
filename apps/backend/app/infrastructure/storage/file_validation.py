"""Validacion de archivos de imagen (Prompt Maestro §20/§27): extension, tipo MIME,
tamano y decodificabilidad real (una imagen corrupta o con extension falsificada se
rechaza aqui, antes de llegar a StoragePort o a AIProvider)."""

import io

from PIL import Image, UnidentifiedImageError

from app.domain.exceptions import ValidationError

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}


def validate_image_file(
    *, filename: str, content_type: str, file_bytes: bytes, max_size_mb: int
) -> None:
    if not file_bytes:
        raise ValidationError("El archivo esta vacio")

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValidationError(f"El archivo supera el limite de {max_size_mb} MB")

    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Extension no permitida: {extension!r}")

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(f"Tipo de archivo no permitido: {content_type!r}")

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("El archivo no es una imagen valida o esta corrupto") from exc
