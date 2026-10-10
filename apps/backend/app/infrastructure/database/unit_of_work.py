from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.config import get_settings
from app.infrastructure.database.lancedb_chunk_repository import LanceDbNormativaChunkRepository
from app.infrastructure.database.repositories.ai_repository import (
    SqlAlchemyAIMessageRepository,
    SqlAlchemyAISessionRepository,
    SqlAlchemyAIToolCallRepository,
)
from app.infrastructure.database.repositories.identity_repository import (
    SqlAlchemyPasswordResetTokenRepository,
    SqlAlchemyPermissionRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyUserRepository,
)
from app.infrastructure.database.repositories.practice_repository import (
    SqlAlchemyPracticeCategoryRepository,
    SqlAlchemyPracticeNarrationRepository,
    SqlAlchemyPracticeRepository,
    SqlAlchemyPracticeTagRepository,
)
from app.infrastructure.database.repositories.progress_repository import (
    SqlAlchemyPracticeEvaluationRepository,
    SqlAlchemyPracticeSubmissionRepository,
    SqlAlchemyStudentPracticeAttemptRepository,
    SqlAlchemyStudentProgressRepository,
)
from app.infrastructure.database.repositories.rag_repository import (
    SqlAlchemyRagEvaluationRunRepository,
)
from app.infrastructure.database.repositories.system_repository import (
    SqlAlchemyAuditLogRepository,
    SqlAlchemyConfigurationRepository,
)
from app.infrastructure.database.session import SessionLocal


class SqlAlchemyUnitOfWork:
    """Implementacion de UnitOfWork (application/ports). Cada `with` abre una sesion y
    repositorios bindeados a ella; el commit/rollback es explicito en el caso de uso.

    `normativa_chunks` es la excepcion: no vive en esta sesion de Postgres sino en
    una tabla LanceDB embebida (ver docs/saturdays_ai/00-plan.md §5 y
    app.infrastructure.database.lancedb_chunk_repository) — `lancedb_path` se toma
    de Settings por defecto (mismo patron que storage_local_path/get_storage_port),
    con un parametro opcional para que las pruebas puedan apuntar a un directorio
    aislado sin tocar el de desarrollo."""

    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
        lancedb_path: str | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._lancedb_path = lancedb_path or get_settings().lancedb_path
        self._session: Session | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        self.roles = SqlAlchemyRoleRepository(self._session)
        self.permissions = SqlAlchemyPermissionRepository(self._session)
        self.password_reset_tokens = SqlAlchemyPasswordResetTokenRepository(self._session)
        self.practices = SqlAlchemyPracticeRepository(self._session)
        self.practice_categories = SqlAlchemyPracticeCategoryRepository(self._session)
        self.practice_tags = SqlAlchemyPracticeTagRepository(self._session)
        self.practice_narrations = SqlAlchemyPracticeNarrationRepository(self._session)
        self.practice_attempts = SqlAlchemyStudentPracticeAttemptRepository(self._session)
        self.practice_submissions = SqlAlchemyPracticeSubmissionRepository(self._session)
        self.practice_evaluations = SqlAlchemyPracticeEvaluationRepository(self._session)
        self.student_progress = SqlAlchemyStudentProgressRepository(self._session)
        self.configurations = SqlAlchemyConfigurationRepository(self._session)
        self.audit_logs = SqlAlchemyAuditLogRepository(self._session)
        self.ai_sessions = SqlAlchemyAISessionRepository(self._session)
        self.ai_messages = SqlAlchemyAIMessageRepository(self._session)
        self.ai_tool_calls = SqlAlchemyAIToolCallRepository(self._session)
        self.normativa_chunks = LanceDbNormativaChunkRepository(self._lancedb_path)
        self.rag_evaluation_runs = SqlAlchemyRagEvaluationRunRepository(self._session)
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        assert self._session is not None
        if exc_type is not None:
            self._session.rollback()
        self._session.close()
        self._session = None

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()

    def rollback(self) -> None:
        assert self._session is not None
        self._session.rollback()
