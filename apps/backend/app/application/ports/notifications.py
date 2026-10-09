from typing import Protocol


class EmailSender(Protocol):
    def send_password_reset_email(self, *, to_email: str, full_name: str, reset_url: str) -> None:
        """Envia el correo con el enlace de restablecimiento. No lanza si el email no
        existe (ese caso se filtra antes, en el caso de uso)."""
        ...
