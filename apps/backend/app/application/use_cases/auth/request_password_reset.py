import hashlib
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.application.ports.notifications import EmailSender
from app.application.ports.unit_of_work import UnitOfWork
from app.domain.entities.identity import PasswordResetToken
from app.infrastructure.config import Settings


class RequestPasswordResetUseCase:
    """Genera un token de un solo uso y envia el enlace de restablecimiento por email.
    Por diseno no revela si el email existe o no (evita enumeracion de usuarios): se
    responde igual tanto si el usuario existe como si no."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        email_sender: EmailSender,
        settings: Settings,
    ) -> None:
        self._uow_factory = uow_factory
        self._email_sender = email_sender
        self._settings = settings

    def execute(self, *, email: str) -> None:
        normalized_email = email.strip().lower()
        with self._uow_factory() as uow:
            user = uow.users.get_by_email(normalized_email)
            if user is None or not user.is_active:
                return

            uow.password_reset_tokens.delete_for_user(user.id)

            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            # Naive UTC: la columna es TIMESTAMP WITHOUT TIME ZONE y se relee como naive
            # en ResetPasswordUseCase, donde se compara contra la hora actual.
            expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                seconds=self._settings.password_reset_token_expires_seconds
            )
            uow.password_reset_tokens.add(
                PasswordResetToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
            )
            uow.commit()

        reset_url = f"{self._settings.frontend_url}/restablecer-contrasena?token={raw_token}"
        self._email_sender.send_password_reset_email(
            to_email=user.email, full_name=user.full_name, reset_url=reset_url
        )
