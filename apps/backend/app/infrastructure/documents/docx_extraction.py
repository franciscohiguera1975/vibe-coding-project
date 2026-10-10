"""Validacion y extraccion de texto de archivos Word (.docx) para el flujo de
carga de ValidateSyllabus (docs/saturdays_ai/00-plan.md §6): mismo espiritu que
`file_validation.validate_image_file` — la extension declarada y el intento real
de abrir el archivo con la libreria correspondiente (aqui, python-docx) son
ambos parte de la validacion, no solo la extension (un .doc o .pdf renombrado a
.docx se rechaza aqui, antes de llegar al caso de uso de validacion de silabos).
"""

import io
import zipfile

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

from app.domain.exceptions import ValidationError

ALLOWED_DOCX_EXTENSIONS = {".docx"}


def validate_and_extract_docx_text(*, filename: str, file_bytes: bytes, max_size_mb: int) -> str:
    """Valida que `file_bytes` sea un .docx real y legible, y devuelve el texto
    de todos los parrafos del cuerpo del documento, unidos con saltos de linea
    (parrafos vacios se omiten). No preserva tablas ni formato: alcanza para
    pasarlo como texto plano al mismo ValidateSyllabusUseCase que ya usa el
    flujo de texto pegado."""
    if not file_bytes:
        raise ValidationError("El archivo esta vacio")

    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValidationError(f"El archivo supera el limite de {max_size_mb} MB")

    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_DOCX_EXTENSIONS:
        raise ValidationError(
            f"Extension no permitida: {extension!r}. Solo se aceptan archivos .docx"
        )

    try:
        document = Document(io.BytesIO(file_bytes))
    except (PackageNotFoundError, zipfile.BadZipFile, KeyError, ValueError) as exc:
        raise ValidationError(
            "El archivo no es un documento Word (.docx) valido o esta corrupto"
        ) from exc

    text = "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    if not text.strip():
        raise ValidationError("El documento Word no contiene texto para validar")
    return text
