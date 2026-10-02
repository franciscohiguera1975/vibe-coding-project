import pytest

from app.application.dto.practice_dto import CreatePracticeInput
from app.application.dto.user_dto import CreateUserInput
from app.application.use_cases.practices.create_practice import CreatePracticeUseCase
from app.application.use_cases.practices.evaluate_practice import EvaluatePracticeUseCase
from app.application.use_cases.practices.get_practice import GetPracticeUseCase
from app.application.use_cases.practices.list_practices import ListPracticesUseCase
from app.application.use_cases.practices.publish_practice import PublishPracticeUseCase
from app.application.use_cases.practices.start_practice import StartPracticeUseCase
from app.application.use_cases.practices.submit_practice import SubmitPracticeUseCase
from app.application.use_cases.users.assign_role import AssignRoleUseCase
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.domain.entities.identity import User
from app.domain.entities.practice import PracticeStatus
from app.domain.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.domain.repositories.practice_repository import PracticeFilters
from app.domain.value_objects.pagination import PageRequest
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.evaluation.rule_based_adapter import RuleBasedEvaluationAdapter
from app.infrastructure.security.password_hasher import BcryptPasswordHasher


@pytest.fixture
def mru_practice_input() -> CreatePracticeInput:
    """Deriva de la Guia 18 (MRU: distancia = velocidad x tiempo)."""
    return CreatePracticeInput(
        title="Simulacion de movimiento rectilineo uniforme",
        type="software",
        description="Predecir, ajustar y observar distancia = velocidad x tiempo.",
        objectives=["Interpretar una formula como relacion experimentable"],
        instructions="Prediga la distancia, ajuste velocidad y tiempo, ejecute y compare.",
        content={
            "model": "distance = speed * time",
            "speed_range": [0, 100],
            "time_range": [0, 3],
        },
        evaluation={
            "strategy": "numeric_match",
            "checks": [
                {"field": "distance_km", "expected": 120, "tolerance": 0.01},
                {"field": "distance_km_2", "expected": 0, "tolerance": 0.01},
            ],
        },
        technologies=["javascript"],
    )


def test_create_practice_requires_permission(student_role, mru_practice_input):
    use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    powerless = User(email="s@x.dev", password_hash="x", full_name="S", roles=[student_role])
    with pytest.raises(PermissionDeniedError):
        use_case.execute(actor=powerless, data=mru_practice_input)


def test_create_practice_rejects_duplicate_slug(admin_user, mru_practice_input):
    use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    use_case.execute(actor=admin_user, data=mru_practice_input)
    with pytest.raises(ConflictError):
        use_case.execute(actor=admin_user, data=mru_practice_input)


def test_publish_requires_instructions_and_content(admin_user):
    create_use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    practice = create_use_case.execute(
        actor=admin_user,
        data=CreatePracticeInput(title="Vacia", type="software", instructions="", content={}),
    )
    publish_use_case = PublishPracticeUseCase(SqlAlchemyUnitOfWork)
    with pytest.raises(ValidationError):
        publish_use_case.execute(actor=admin_user, practice_id=practice.id)


def test_get_practice_hides_draft_from_public(admin_user, mru_practice_input):
    create_use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    practice = create_use_case.execute(actor=admin_user, data=mru_practice_input)

    get_use_case = GetPracticeUseCase(SqlAlchemyUnitOfWork)
    with pytest.raises(NotFoundError):
        get_use_case.execute(slug=practice.slug, actor=None)

    # El admin (con practice:read) si puede previsualizar el borrador.
    fetched = get_use_case.execute(slug=practice.slug, actor=admin_user)
    assert fetched.slug == practice.slug


def test_list_practices_forces_published_filter_for_public(admin_user, mru_practice_input):
    create_use_case = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    create_use_case.execute(actor=admin_user, data=mru_practice_input)

    list_use_case = ListPracticesUseCase(SqlAlchemyUnitOfWork)
    public_page = list_use_case.execute(
        actor=None, filters=PracticeFilters(), page_request=PageRequest()
    )
    assert public_page.total == 0  # sigue en draft

    admin_page = list_use_case.execute(
        actor=admin_user, filters=PracticeFilters(), page_request=PageRequest()
    )
    assert admin_page.total == 1


def test_full_execution_flow_start_submit_evaluate(admin_user, student_role, mru_practice_input):
    create_practice = CreatePracticeUseCase(SqlAlchemyUnitOfWork)
    practice = create_practice.execute(actor=admin_user, data=mru_practice_input)
    PublishPracticeUseCase(SqlAlchemyUnitOfWork).execute(actor=admin_user, practice_id=practice.id)

    hasher = BcryptPasswordHasher()
    student = CreateUserUseCase(SqlAlchemyUnitOfWork, hasher).execute(
        actor=admin_user,
        data=CreateUserInput(
            email="student1@vibe-coding-platform.dev", full_name="Est", password="Password123!"
        ),
    )
    student = AssignRoleUseCase(SqlAlchemyUnitOfWork).execute(
        actor=admin_user, user_id=student.id, role_name="STUDENT"
    )

    start_use_case = StartPracticeUseCase(SqlAlchemyUnitOfWork)
    attempt = start_use_case.execute(actor=student, practice_slug=practice.slug)
    assert attempt.attempt_number == 1

    submit_use_case = SubmitPracticeUseCase(SqlAlchemyUnitOfWork)
    submission = submit_use_case.execute(
        actor=student,
        attempt_id=attempt.id,
        payload={"distance_km": 120, "distance_km_2": 0},
    )

    evaluate_use_case = EvaluatePracticeUseCase(SqlAlchemyUnitOfWork, RuleBasedEvaluationAdapter())
    evaluation = evaluate_use_case.execute(actor=student, submission_id=submission.id)
    assert evaluation.passed is True
    assert evaluation.score == 100.0

    with SqlAlchemyUnitOfWork() as uow:
        progress = uow.student_progress.get_by_user_and_practice(student.id, practice.id)
        assert progress.status.value == "completed"
        assert progress.best_score == 100.0

        updated_practice = uow.practices.get_by_id(practice.id)
        assert updated_practice.status == PracticeStatus.PUBLISHED
