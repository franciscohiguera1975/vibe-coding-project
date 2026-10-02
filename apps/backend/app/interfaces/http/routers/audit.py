from fastapi import APIRouter, Depends, Query

from app.application.use_cases.audit.list_audit_logs import ListAuditLogsUseCase
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.value_objects.pagination import PageRequest
from app.interfaces.http.controllers.system_controller import audit_log_page_to_response
from app.interfaces.http.dependencies.admin_use_cases import get_list_audit_logs_use_case
from app.interfaces.http.dependencies.auth import require_permission
from app.interfaces.http.schemas.audit import AuditLogListResponse

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    actor: User = Depends(require_permission(perm.AUDIT_READ)),
    use_case: ListAuditLogsUseCase = Depends(get_list_audit_logs_use_case),
) -> AuditLogListResponse:
    result = use_case.execute(actor=actor, page_request=PageRequest(page=page, page_size=page_size))
    return audit_log_page_to_response(result)
