"""SmtpEmailAdapter: implementacion de EmailSender que envia correo real via SMTP
(EMAIL_PROVIDER=smtp, ver SMTP_* en .env.example). Usa smtplib de la libreria estandar,
sin dependencias adicionales."""

import smtplib
from email.message import EmailMessage


class SmtpEmailAdapter:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        from_address: str,
        use_tls: bool,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_address = from_address
        self._use_tls = use_tls

    def send_password_reset_email(self, *, to_email: str, full_name: str, reset_url: str) -> None:
        message = EmailMessage()
        message["Subject"] = "Restablecer contraseña - Vibe Coding Platform"
        message["From"] = self._from_address
        message["To"] = to_email
        message.set_content(
            f"Hola {full_name},\n\n"
            "Recibimos una solicitud para restablecer tu contraseña en Vibe Coding "
            "Platform. Si no fuiste tú, ignora este mensaje.\n\n"
            f"Para continuar, abre este enlace (valido por tiempo limitado):\n{reset_url}\n"
        )

        with smtplib.SMTP(self._host, self._port, timeout=10) as smtp:
            if self._use_tls:
                smtp.starttls()
            if self._username:
                smtp.login(self._username, self._password)
            smtp.send_message(message)
