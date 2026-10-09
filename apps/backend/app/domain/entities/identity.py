import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Permission:
    code: str
    description: str = ""
    id: uuid.UUID | None = None


@dataclass(slots=True)
class Role:
    name: str
    description: str = ""
    id: uuid.UUID | None = None
    permissions: list[Permission] = field(default_factory=list)

    def has_permission(self, code: str) -> bool:
        return any(p.code == code for p in self.permissions)


@dataclass(slots=True)
class User:
    email: str
    password_hash: str
    full_name: str
    id: uuid.UUID | None = None
    is_active: bool = True
    roles: list[Role] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def has_permission(self, code: str) -> bool:
        return any(role.has_permission(code) for role in self.roles)

    def has_role(self, name: str) -> bool:
        return any(role.name == name for role in self.roles)


@dataclass(slots=True)
class PasswordResetToken:
    """Token de un solo uso para restablecer contraseña. Se persiste el hash (sha256),
    nunca el token en claro que recibe el usuario por email."""

    user_id: uuid.UUID
    token_hash: str
    expires_at: datetime
    id: uuid.UUID | None = None
    used_at: datetime | None = None
    created_at: datetime | None = None

    def is_valid(self, *, now: datetime) -> bool:
        return self.used_at is None and self.expires_at > now
