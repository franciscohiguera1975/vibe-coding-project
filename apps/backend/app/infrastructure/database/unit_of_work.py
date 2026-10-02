from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.repositories.identity_repository import (
    SqlAlchemyPermissionRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyUserRepository,
)
from app.infrastructure.database.repositories.practice_repository import (
    SqlAlchemyPracticeCategoryRepository,
    SqlAlchemyPracticeRepository,
    SqlAlchemyPracticeTagRepository,
)
from app.infrastructure.database.repositories.progress_repository import (
    SqlAlchemyPracticeEvaluationRepository,
    SqlAlchemyPracticeSubmissionRepository,
    SqlAlchemyStudentPracticeAttemptRepository,
    SqlAlchemyStudentProgressRepository,
)
from app.infrastructure.database.repositories.system_repository import (
    SqlAlchemyConfigurationRepository,
)
from app.infrastructure.database.session import SessionLocal


class SqlAlchemyUnitOfWork:
    """Implementacion de UnitOfWork (application/ports). Cada `with` abre una sesion y
    repositorios bindeados a ella; el commit/rollback es explicito en el caso de uso."""

    def __init__(self, session_factory: sessionmaker[Session] = SessionLocal) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        self.roles = SqlAlchemyRoleRepository(self._session)
        self.permissions = SqlAlchemyPermissionRepository(self._session)
        self.practices = SqlAlchemyPracticeRepository(self._session)
        self.practice_categories = SqlAlchemyPracticeCategoryRepository(self._session)
        self.practice_tags = SqlAlchemyPracticeTagRepository(self._session)
        self.practice_attempts = SqlAlchemyStudentPracticeAttemptRepository(self._session)
        self.practice_submissions = SqlAlchemyPracticeSubmissionRepository(self._session)
        self.practice_evaluations = SqlAlchemyPracticeEvaluationRepository(self._session)
        self.student_progress = SqlAlchemyStudentProgressRepository(self._session)
        self.configurations = SqlAlchemyConfigurationRepository(self._session)
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
