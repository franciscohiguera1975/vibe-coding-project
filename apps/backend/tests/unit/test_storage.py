import io
import tempfile

import pytest
from PIL import Image

from app.domain.exceptions import NotFoundError, ValidationError
from app.infrastructure.storage.file_validation import validate_image_file
from app.infrastructure.storage.local_adapter import LocalStorageAdapter


def _png_bytes() -> bytes:
    image = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_validate_image_file_accepts_valid_png():
    validate_image_file(
        filename="foto.png", content_type="image/png", file_bytes=_png_bytes(), max_size_mb=5
    )


def test_validate_image_file_rejects_empty_file():
    with pytest.raises(ValidationError):
        validate_image_file(
            filename="foto.png", content_type="image/png", file_bytes=b"", max_size_mb=5
        )


def test_validate_image_file_rejects_oversized_file():
    with pytest.raises(ValidationError):
        validate_image_file(
            filename="foto.png",
            content_type="image/png",
            file_bytes=_png_bytes() * 500_000,
            max_size_mb=1,
        )


def test_validate_image_file_rejects_disallowed_extension():
    with pytest.raises(ValidationError):
        validate_image_file(
            filename="foto.gif", content_type="image/gif", file_bytes=_png_bytes(), max_size_mb=5
        )


def test_validate_image_file_rejects_corrupt_bytes_disguised_as_png():
    with pytest.raises(ValidationError):
        validate_image_file(
            filename="foto.png",
            content_type="image/png",
            file_bytes=b"not-a-real-image",
            max_size_mb=5,
        )


def test_local_storage_adapter_roundtrip():
    with tempfile.TemporaryDirectory() as tmp_dir:
        adapter = LocalStorageAdapter(tmp_dir, "http://localhost:3000")
        key = adapter.upload(_png_bytes(), filename="foto.png", content_type="image/png")

        assert key.endswith(".png")
        assert adapter.get_url(key) == f"http://localhost:3000/api/storage/{key}"
        assert adapter.read(key) == _png_bytes()

        adapter.delete(key)
        with pytest.raises(NotFoundError):
            adapter.read(key)


def test_local_storage_adapter_rejects_path_traversal():
    with tempfile.TemporaryDirectory() as tmp_dir:
        adapter = LocalStorageAdapter(tmp_dir, "http://localhost:3000")
        with pytest.raises(NotFoundError):
            adapter.read("../../etc/passwd")
