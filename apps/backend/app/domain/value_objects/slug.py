import re
import unicodedata
from dataclasses import dataclass

from app.domain.exceptions import ValidationError

_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class Slug:
    value: str

    def __post_init__(self) -> None:
        if not _SLUG_RE.match(self.value):
            raise ValidationError(
                f"Slug invalido: {self.value!r} (use minusculas, numeros y guiones)"
            )

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_text(cls, text: str) -> "Slug":
        normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        normalized = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
        return cls(normalized)
