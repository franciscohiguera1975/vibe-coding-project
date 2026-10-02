import bcrypt

from app.domain.exceptions import ValidationError

_MAX_PASSWORD_BYTES = 72


class BcryptPasswordHasher:
    """Implementa application.ports.security.PasswordHasher usando bcrypt directamente
    (sin passlib: la version 1.7.4, sin mantenimiento desde 2020, es incompatible con
    bcrypt>=4.1 — ver https://github.com/pyca/bcrypt/issues/684)."""

    def hash(self, plain_password: str) -> str:
        encoded = plain_password.encode("utf-8")
        if len(encoded) > _MAX_PASSWORD_BYTES:
            raise ValidationError(f"La contraseña no debe superar {_MAX_PASSWORD_BYTES} bytes")
        return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
