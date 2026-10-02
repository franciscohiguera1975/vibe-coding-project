from typing import Protocol

from app.domain.entities.system import Configuration


class ConfigurationRepository(Protocol):
    def get_by_key(self, key: str) -> Configuration | None: ...

    def list_all(self) -> list[Configuration]: ...

    def upsert(self, configuration: Configuration) -> Configuration: ...
