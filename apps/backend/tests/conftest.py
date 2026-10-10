import atexit
import os
import shutil
import tempfile
import uuid
from pathlib import Path

# LANCEDB_PATH debe fijarse ANTES de importar cualquier modulo de `app` (abajo),
# porque app.infrastructure.database.session construye el engine de SQLAlchemy a
# nivel de modulo llamando a get_settings(), que cachea la instancia de Settings
# (@lru_cache) la primera vez que se construye — si este override llegara tarde,
# las pruebas usarian el LANCEDB_PATH real de desarrollo (./storage/lancedb) en
# vez de un directorio aislado y descartable (ver docs/saturdays_ai/00-plan.md §5
# y la nota junto a _clean_lancedb mas abajo).
_TEST_LANCEDB_ROOT = tempfile.mkdtemp(prefix="vibe-coding-test-lancedb-")
os.environ["LANCEDB_PATH"] = _TEST_LANCEDB_ROOT
atexit.register(shutil.rmtree, _TEST_LANCEDB_ROOT, ignore_errors=True)

import pytest  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.domain import permissions as perm  # noqa: E402
from app.domain.entities.identity import Permission, Role, User  # noqa: E402
from app.infrastructure.config import get_settings  # noqa: E402
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork  # noqa: E402
from app.infrastructure.security.password_hasher import BcryptPasswordHasher  # noqa: E402

TRUNCATE_TABLES = (
    "audit_logs",
    "ai_tool_calls",
    "ai_messages",
    "ai_sessions",
    "rag_evaluation_runs",
    "practice_evaluations",
    "practice_submissions",
    "student_practice_attempts",
    "student_progress",
    "practice_narrations",
    "practice_contents",
    "practice_practice_tags",
    "practices",
    "practice_tags",
    "practice_categories",
    "user_roles",
    "role_permissions",
    "password_reset_tokens",
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


@pytest.fixture(autouse=True)
def _clean_lancedb():
    """Equivalente de `_clean_database` para `normativa_chunks`, que ya no vive en
    Postgres (ver docs/saturdays_ai/00-plan.md §5): en vez de TRUNCATE, se borra el
    directorio LanceDB completo antes de cada prueba. `LANCEDB_PATH` ya apunta a un
    directorio temporal exclusivo de esta sesion de pruebas (ver el override al
    inicio de este archivo), asi que esto nunca toca `./storage/lancedb` de
    desarrollo ni dato real."""
    path = Path(get_settings().lancedb_path)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
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
