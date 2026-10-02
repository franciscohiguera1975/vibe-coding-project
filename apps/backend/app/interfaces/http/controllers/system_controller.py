from app.domain.entities.system import AuditLog, Configuration
from app.domain.value_objects.pagination import Page
from app.interfaces.http.schemas.audit import AuditLogListResponse, AuditLogPublic
from app.interfaces.http.schemas.configuration import ConfigurationPublic


def configuration_to_public(configuration: Configuration) -> ConfigurationPublic:
    return ConfigurationPublic(
        key=configuration.key, value=configuration.value, description=configuration.description
    )


def audit_log_to_public(audit_log: AuditLog) -> AuditLogPublic:
    return AuditLogPublic(
        id=str(audit_log.id),
        user_id=str(audit_log.user_id) if audit_log.user_id else None,
        action=audit_log.action,
        entity_type=audit_log.entity_type,
        entity_id=audit_log.entity_id,
        metadata=audit_log.metadata,
        created_at=audit_log.created_at,
    )


def audit_log_page_to_response(page: Page[AuditLog]) -> AuditLogListResponse:
    return AuditLogListResponse(
        items=[audit_log_to_public(a) for a in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )
