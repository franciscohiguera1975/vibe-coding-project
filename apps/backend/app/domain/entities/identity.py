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
