import pytest

from app.application.dto.practice_dto import CreatePracticeInput, UpdatePracticeInput
from app.application.use_cases.practices.create_practice import CreatePracticeUseCase
from app.application.use_cases.practices.generate_practice_narration import (
    GeneratePracticeNarrationUseCase,
)
from app.application.use_cases.practices.get_practice_narration import (
    GetPracticeNarrationUseCase,
)
from app.application.use_cases.practices.publish_practice import PublishPracticeUseCase
from app.application.use_cases.practices.update_practice import UpdatePracticeUseCase
from app.domain.exceptions import NotFoundError, PermissionDeniedError
from app.infrastructure.ai.mock_narration_adapter import MockNarrationAdapter
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.storage.local_adapter import LocalStorageAdapter


@pytest.fixture
def narration_port() -> MockNarrationAdapter:
    return MockNarrationAdapter()


@pytest.fixture
def storage_port(tmp_path) -> LocalStorageAdapter:
    return LocalStorageAdapter(str(tmp_path / "uploads"), "http://localhost:3000")


@pytest.fixture
def published_practice(admin_user):
    create_use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    practice = create_use_case.execute(
        actor=admin_user,
        data=CreatePracticeInput(
            title="Practica narrada",
            type="software",
            instructions="Resuelva el problema de MRU",
            objectives=["Comprender distancia", "Aplicar la formula"],
            content={"model": {"variables": {}}},
        ),
    )
    PublishPracticeUseCase(SqlAlchemyUnitOfWork).execute(actor=admin_user, practice_id=practice.id)
    return practice


class _CountingNarrationAdapter:
    """Envuelve MockNarrationAdapter para contar cuantas veces se invoca synthesize
    (ver objetivo de la prueba de idempotencia: cero llamadas extra en un repeat)."""

    def __init__(self) -> None:
        self.calls = 0
        self._inner = MockNarrationAdapter()

    def synthesize(self, text: str, *, lang: str) -> bytes:
        self.calls += 1
        return self._inner.synthesize(text, lang=lang)


def test_generate_narration_twice_without_changes_calls_synthesize_once(
    admin_user, published_practice, storage_port
):
    """Garantia de control de costo: generar la narracion dos veces para el mismo
    contenido debe invocar NarrationPort.synthesize UNA sola vez en total. Si esto
    falla, el sistema estaria regenerando audio (y por tanto gastando API real) en
    cada visita, que es exactamente lo que el diseño debe evitar."""
    counting_adapter = _CountingNarrationAdapter()
    use_case = GeneratePracticeNarrationUseCase(
        SqlAlchemyUnitOfWork, counting_adapter, storage_port
    )

    first = use_case.execute(actor=admin_user, slug=published_practice.slug, lang="es")
    assert first.cached is False
    assert counting_adapter.calls == 1

    second = use_case.execute(actor=admin_user, slug=published_practice.slug, lang="es")
    assert second.cached is True
    assert counting_adapter.calls == 1, (
        "synthesize() fue llamado de nuevo pese a que el texto fuente no cambio: "
        "esto rompe la garantia de control de costo de la narracion"
    )
    assert second.storage_key == first.storage_key


def test_generate_narration_after_content_change_resynthesizes(
    admin_user, published_practice, storage_port
):
    counting_adapter = _CountingNarrationAdapter()
    use_case = GeneratePracticeNarrationUseCase(
        SqlAlchemyUnitOfWork, counting_adapter, storage_port
    )

    first = use_case.execute(actor=admin_user, slug=published_practice.slug, lang="es")
    assert counting_adapter.calls == 1

    UpdatePracticeUseCase(SqlAlchemyUnitOfWork).execute(
        actor=admin_user,
        practice_id=published_practice.id,
        data=UpdatePracticeInput(instructions="Instrucciones completamente distintas"),
    )

    second = use_case.execute(actor=admin_user, slug=published_practice.slug, lang="es")
    assert second.cached is False
    assert counting_adapter.calls == 2
    assert second.storage_key != first.storage_key


def test_generate_narration_requires_permission(
    published_practice, student_role, password_hasher, storage_port
):
    from app.domain.entities.identity import User

    student = User(
        email="student-narration@vibe-coding-platform.dev",
        password_hash=password_hasher.hash("Password123!"),
        full_name="Estudiante",
        roles=[student_role],
    )
    use_case = GeneratePracticeNarrationUseCase(
        SqlAlchemyUnitOfWork, MockNarrationAdapter(), storage_port
    )
    with pytest.raises(PermissionDeniedError):
        use_case.execute(actor=student, slug=published_practice.slug, lang="es")


def test_get_narration_raises_not_found_before_generation(published_practice):
    use_case = GetPracticeNarrationUseCase(SqlAlchemyUnitOfWork)
    with pytest.raises(NotFoundError):
        use_case.execute(slug=published_practice.slug, lang="es")


def test_get_narration_returns_row_after_generation(admin_user, published_practice, storage_port):
    generate_use_case = GeneratePracticeNarrationUseCase(
        SqlAlchemyUnitOfWork, MockNarrationAdapter(), storage_port
    )
    generate_use_case.execute(actor=admin_user, slug=published_practice.slug, lang="es")

    get_use_case = GetPracticeNarrationUseCase(SqlAlchemyUnitOfWork)
    narration = get_use_case.execute(slug=published_practice.slug, lang="es")
    assert narration.lang == "es"
    assert narration.storage_key
