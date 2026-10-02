from typing import Protocol

from app.domain.entities.system import AuditLog, Configuration
from app.domain.value_objects.pagination import Page, PageRequest


class ConfigurationRepository(Protocol):
    def get_by_key(self, key: str) -> Configuration | None: ...

    def list_all(self) -> list[Configuration]: ...

    def upsert(self, configuration: Configuration) -> Configuration: ...


class AuditLogRepository(Protocol):
    def add(self, audit_log: AuditLog) -> AuditLog: ...

    def list(self, page_request: PageRequest) -> Page[AuditLog]: ...
