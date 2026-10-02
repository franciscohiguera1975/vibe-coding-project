import pytest

from app.application.dto.user_dto import CreateUserInput
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.roles.assign_permission import AssignPermissionUseCase
from app.application.use_cases.users.assign_role import AssignRoleUseCase
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.exceptions import ConflictError, InvalidCredentialsError, PermissionDeniedError
from app.infrastructure.config import get_settings
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.token_service import JoseTokenService


@pytest.fixture
def token_service() -> JoseTokenService:
    return JoseTokenService(get_settings())


def test_login_succeeds_with_correct_credentials(admin_user, password_hasher, token_service):
    use_case = LoginUseCase(SqlAlchemyUnitOfWork, password_hasher, token_service)
    tokens = use_case.execute(email="admin@vibe-coding-platform.dev", password="AdminPass123!")
    assert tokens.user.email == "admin@vibe-coding-platform.dev"
    assert tokens.access_token
    assert tokens.refresh_token


def test_login_fails_with_wrong_password(admin_user, password_hasher, token_service):
    use_case = LoginUseCase(SqlAlchemyUnitOfWork, password_hasher, token_service)
    with pytest.raises(InvalidCredentialsError):
        use_case.execute(email="admin@vibe-coding-platform.dev", password="wrong")


def test_login_fails_for_unknown_email(password_hasher, token_service):
    use_case = LoginUseCase(SqlAlchemyUnitOfWork, password_hasher, token_service)
    with pytest.raises(InvalidCredentialsError):
        use_case.execute(email="nobody@vibe-coding-platform.dev", password="whatever")


def test_refresh_token_rotates_tokens(admin_user, password_hasher, token_service):
    login_use_case = LoginUseCase(SqlAlchemyUnitOfWork, password_hasher, token_service)
    tokens = login_use_case.execute(
        email="admin@vibe-coding-platform.dev", password="AdminPass123!"
    )

    refresh_use_case = RefreshTokenUseCase(SqlAlchemyUnitOfWork, token_service)
    new_tokens = refresh_use_case.execute(refresh_token=tokens.refresh_token)

    assert new_tokens.access_token != tokens.access_token
    assert new_tokens.user.id == tokens.user.id


def test_refresh_token_rejects_access_token(admin_user, password_hasher, token_service):
    login_use_case = LoginUseCase(SqlAlchemyUnitOfWork, password_hasher, token_service)
    tokens = login_use_case.execute(
        email="admin@vibe-coding-platform.dev", password="AdminPass123!"
    )

    refresh_use_case = RefreshTokenUseCase(SqlAlchemyUnitOfWork, token_service)
    with pytest.raises(InvalidCredentialsError):
        refresh_use_case.execute(refresh_token=tokens.access_token)


def test_create_user_requires_permission(admin_user, password_hasher, random_email):
    use_case = CreateUserUseCase(SqlAlchemyUnitOfWork, password_hasher)
    powerless_actor = User(
        email="nobody@vibe-coding-platform.dev", password_hash="x", full_name="Nadie", roles=[]
    )
    with pytest.raises(PermissionDeniedError):
        use_case.execute(
            actor=powerless_actor,
            data=CreateUserInput(email=random_email, full_name="Nuevo", password="Password123!"),
        )


def test_create_user_rejects_duplicate_email(admin_user, password_hasher):
    use_case = CreateUserUseCase(SqlAlchemyUnitOfWork, password_hasher)
    with pytest.raises(ConflictError):
        use_case.execute(
            actor=admin_user,
            data=CreateUserInput(
                email="admin@vibe-coding-platform.dev",
                full_name="Duplicado",
                password="Password123!",
            ),
        )


def test_assign_role_adds_role_to_user(admin_user, student_role, password_hasher, random_email):
    create_use_case = CreateUserUseCase(SqlAlchemyUnitOfWork, password_hasher)
    new_user = create_use_case.execute(
        actor=admin_user,
        data=CreateUserInput(
            email=random_email, full_name="Nuevo Estudiante", password="Password123!"
        ),
    )
    assert new_user.roles == []

    assign_use_case = AssignRoleUseCase(SqlAlchemyUnitOfWork)
    updated = assign_use_case.execute(actor=admin_user, user_id=new_user.id, role_name="STUDENT")
    assert any(r.name == "STUDENT" for r in updated.roles)


def test_assign_permission_adds_permission_to_role(admin_user, student_role):
    use_case = AssignPermissionUseCase(SqlAlchemyUnitOfWork)
    updated = use_case.execute(
        actor=admin_user, role_name="STUDENT", permission_code=perm.PRACTICE_CREATE
    )
    assert any(p.code == perm.PRACTICE_CREATE for p in updated.permissions)
