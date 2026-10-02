from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.system import Configuration
from app.infrastructure.database.models.system import ConfigurationModel


def _to_domain(model: ConfigurationModel) -> Configuration:
    return Configuration(
        id=model.id, key=model.key, value=dict(model.value), description=model.description
    )


class SqlAlchemyConfigurationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_key(self, key: str) -> Configuration | None:
        model = self._session.scalar(
            select(ConfigurationModel).where(ConfigurationModel.key == key)
        )
        return _to_domain(model) if model else None

    def list_all(self) -> list[Configuration]:
        rows = self._session.scalars(select(ConfigurationModel).order_by(ConfigurationModel.key))
        return [_to_domain(m) for m in rows]

    def upsert(self, configuration: Configuration) -> Configuration:
        model = self._session.scalar(
            select(ConfigurationModel).where(ConfigurationModel.key == configuration.key)
        )
        if model is None:
            model = ConfigurationModel(
                key=configuration.key,
                value=dict(configuration.value),
                description=configuration.description,
            )
            self._session.add(model)
        else:
            model.value = dict(configuration.value)
            model.description = configuration.description
        self._session.flush()
        return _to_domain(model)
