import re
from dataclasses import dataclass

from app.domain.exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.value):
            raise ValidationError(f"Email invalido: {self.value!r}")
        object.__setattr__(self, "value", self.value.strip().lower())

    def __str__(self) -> str:
        return self.value
