from typing import Protocol

from app.domain.repositories.ai_repository import (
    AIMessageRepository,
    AISessionRepository,
    AIToolCallRepository,
)
from app.domain.repositories.identity_repository import (
    PermissionRepository,
    RoleRepository,
    UserRepository,
)
from app.domain.repositories.practice_repository import (
    PracticeCategoryRepository,
    PracticeRepository,
    PracticeTagRepository,
)
from app.domain.repositories.progress_repository import (
    PracticeEvaluationRepository,
    PracticeSubmissionRepository,
    StudentPracticeAttemptRepository,
    StudentProgressRepository,
)
from app.domain.repositories.system_repository import AuditLogRepository, ConfigurationRepository


class UnitOfWork(Protocol):
    """Limite transaccional explicito (recomendado en la validacion de arquitectura):
    los casos de uso que tocan varios repositorios lo hacen dentro de un `with uow:`,
    y el commit/rollback ocurre aqui, no dentro de cada repositorio."""

    users: UserRepository
    roles: RoleRepository
    permissions: PermissionRepository
    practices: PracticeRepository
    practice_categories: PracticeCategoryRepository
    practice_tags: PracticeTagRepository
    practice_attempts: StudentPracticeAttemptRepository
    practice_submissions: PracticeSubmissionRepository
    practice_evaluations: PracticeEvaluationRepository
    student_progress: StudentProgressRepository
    configurations: ConfigurationRepository
    audit_logs: AuditLogRepository
    ai_sessions: AISessionRepository
    ai_messages: AIMessageRepository
    ai_tool_calls: AIToolCallRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
