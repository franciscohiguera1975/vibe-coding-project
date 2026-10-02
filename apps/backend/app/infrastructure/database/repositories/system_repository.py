from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.system import AuditLog, Configuration
from app.domain.value_objects.pagination import Page, PageRequest
from app.infrastructure.database.models.system import AuditLogModel, ConfigurationModel


def _to_domain(model: ConfigurationModel) -> Configuration:
    return Configuration(
        id=model.id, key=model.key, value=dict(model.value), description=model.description
    )


def _audit_log_to_domain(model: AuditLogModel) -> AuditLog:
    return AuditLog(
        id=model.id,
        user_id=model.user_id,
        action=model.action,
        entity_type=model.entity_type,
        entity_id=model.entity_id,
        metadata=dict(model.audit_metadata),
        ip_address=model.ip_address,
        created_at=model.created_at,
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


class SqlAlchemyAuditLogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, audit_log: AuditLog) -> AuditLog:
        model = AuditLogModel(
            user_id=audit_log.user_id,
            action=audit_log.action,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            audit_metadata=dict(audit_log.metadata),
            ip_address=audit_log.ip_address,
            created_at=audit_log.created_at,
        )
        self._session.add(model)
        self._session.flush()
        return _audit_log_to_domain(model)

    def list(self, page_request: PageRequest) -> Page[AuditLog]:
        total = self._session.scalar(select(func.count()).select_from(AuditLogModel)) or 0
        rows = self._session.scalars(
            select(AuditLogModel)
            .order_by(AuditLogModel.created_at.desc())
            .offset(page_request.offset)
            .limit(page_request.page_size)
        )
        return Page(
            items=[_audit_log_to_domain(m) for m in rows],
            total=total,
            page=page_request.page,
            page_size=page_request.page_size,
        )
