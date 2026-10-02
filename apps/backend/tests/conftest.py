import uuid

import pytest
from sqlalchemy import text

from app.domain import permissions as perm
from app.domain.entities.identity import Permission, Role, User
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

TRUNCATE_TABLES = (
    "audit_logs",
    "ai_tool_calls",
    "ai_messages",
    "ai_sessions",
    "practice_evaluations",
    "practice_submissions",
    "student_practice_attempts",
    "student_progress",
    "practice_contents",
    "practice_practice_tags",
    "practices",
    "practice_tags",
    "practice_categories",
    "user_roles",
    "role_permissions",
    "users",
    "roles",
    "permissions",
    "configurations",
)


@pytest.fixture(autouse=True)
def _clean_database():
    """Las pruebas usan la base de datos real de desarrollo (Postgres via docker-compose,
    ver AI_PROVIDER=mock en .env para que nada dependa de un proveedor externo); se
    trunca antes de cada prueba para aislarlas."""
    with SqlAlchemyUnitOfWork() as uow:
        uow._session.execute(text(f"TRUNCATE TABLE {', '.join(TRUNCATE_TABLES)} CASCADE"))
        uow.commit()
    yield


@pytest.fixture
def password_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


@pytest.fixture
def admin_user(password_hasher: BcryptPasswordHasher) -> User:
    with SqlAlchemyUnitOfWork() as uow:
        all_perms = [
            uow.permissions.add(Permission(code=code, description=desc))
            for code, desc in perm.ALL_PERMISSIONS.items()
        ]
        role = uow.roles.add(Role(name="ADMIN", description="Administrador", permissions=all_perms))
        user = uow.users.add(
            User(
                email="admin@vibe-coding-platform.dev",
                password_hash=password_hasher.hash("AdminPass123!"),
                full_name="Admin de prueba",
                roles=[role],
            )
        )
        uow.commit()
        return user


@pytest.fixture
def student_role() -> Role:
    with SqlAlchemyUnitOfWork() as uow:
        read_perm = uow.permissions.get_by_code(perm.PRACTICE_READ)
        if read_perm is None:
            read_perm = uow.permissions.add(
                Permission(code=perm.PRACTICE_READ, description="Leer practicas")
            )
        role = uow.roles.add(
            Role(name="STUDENT", description="Estudiante", permissions=[read_perm])
        )
        uow.commit()
        return role


@pytest.fixture
def random_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@vibe-coding-platform.dev"
