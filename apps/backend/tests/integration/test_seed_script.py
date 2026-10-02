import subprocess
import sys
from pathlib import Path

from sqlalchemy import func, select

from app.infrastructure.database.models.identity import PermissionModel, RoleModel, UserModel
from app.infrastructure.database.models.practice import PracticeModel
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
SEED_SCRIPT = BACKEND_DIR / "scripts" / "seed.py"


def _run_seed() -> None:
    result = subprocess.run(
        [sys.executable, str(SEED_SCRIPT)], cwd=BACKEND_DIR, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_seed_is_idempotent_and_creates_expected_data():
    _run_seed()
    _run_seed()

    with SqlAlchemyUnitOfWork() as uow:
        session = uow._session
        assert session.scalar(select(func.count()).select_from(UserModel)) == 1
        assert session.scalar(select(func.count()).select_from(RoleModel)) == 4
        assert session.scalar(select(func.count()).select_from(PermissionModel)) == 12
        assert session.scalar(select(func.count()).select_from(PracticeModel)) == 4

        admin = uow.users.get_by_email("admin@vibecoding-platform.dev")
        assert admin is not None
        assert admin.has_role("ADMIN")

        slugs = {p.slug for p in session.query(PracticeModel).all()}
        assert slugs == {
            "software-01-simulacion-mru",
            "software-02-depuracion-mru",
            "image-01-conteo-circulos",
            "image-02-diagnostico-errores",
        }
