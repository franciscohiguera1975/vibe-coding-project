from functools import lru_cache

from app.application.ports.notifications import EmailSender
from app.infrastructure.config import get_settings
from app.infrastructure.email.console_adapter import ConsoleEmailAdapter


@lru_cache
def get_email_sender() -> EmailSender:
    """Selecciona el adaptador segun EMAIL_PROVIDER. console es el default en dev/test
    y no requiere credenciales (mismo patron que get_ai_provider)."""
    settings = get_settings()
    if settings.email_provider == "smtp":
        from app.infrastructure.email.smtp_adapter import SmtpEmailAdapter

        if not settings.smtp_host:
            raise RuntimeError("EMAIL_PROVIDER=smtp requiere SMTP_HOST configurado")
        return SmtpEmailAdapter(
            host=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            from_address=settings.smtp_from,
            use_tls=settings.smtp_use_tls,
        )
    return ConsoleEmailAdapter()
