import pytest

from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.request_password_reset import RequestPasswordResetUseCase
from app.application.use_cases.auth.reset_password import ResetPasswordUseCase
from app.domain.exceptions import InvalidOrExpiredTokenError
from app.infrastructure.config import get_settings
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.token_service import JoseTokenService


class FakeEmailSender:
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    def send_password_reset_email(self, *, to_email: str, full_name: str, reset_url: str) -> None:
        self.sent.append({"to_email": to_email, "full_name": full_name, "reset_url": reset_url})


@pytest.fixture
def email_sender() -> FakeEmailSender:
    return FakeEmailSender()


def _extract_token(reset_url: str) -> str:
    return reset_url.split("token=", 1)[1]


def test_request_password_reset_sends_email_for_existing_user(admin_user, email_sender):
    use_case = RequestPasswordResetUseCase(SqlAlchemyUnitOfWork, email_sender, get_settings())
    use_case.execute(email="admin@vibe-coding-platform.dev")

    assert len(email_sender.sent) == 1
    assert email_sender.sent[0]["to_email"] == "admin@vibe-coding-platform.dev"
    assert "token=" in email_sender.sent[0]["reset_url"]


def test_request_password_reset_is_silent_for_unknown_email(email_sender):
    use_case = RequestPasswordResetUseCase(SqlAlchemyUnitOfWork, email_sender, get_settings())
    use_case.execute(email="nobody@vibe-coding-platform.dev")

    assert email_sender.sent == []


def test_reset_password_changes_password_and_allows_login(
    admin_user, password_hasher, email_sender
):
    request_use_case = RequestPasswordResetUseCase(
        SqlAlchemyUnitOfWork, email_sender, get_settings()
    )
    request_use_case.execute(email="admin@vibe-coding-platform.dev")
    token = _extract_token(email_sender.sent[0]["reset_url"])

    reset_use_case = ResetPasswordUseCase(SqlAlchemyUnitOfWork, password_hasher)
    reset_use_case.execute(token=token, new_password="NuevaClave123!")

    login_use_case = LoginUseCase(
        SqlAlchemyUnitOfWork, password_hasher, JoseTokenService(get_settings())
    )
    tokens = login_use_case.execute(
        email="admin@vibe-coding-platform.dev", password="NuevaClave123!"
    )
    assert tokens.access_token


def test_reset_password_rejects_reused_token(admin_user, password_hasher, email_sender):
    request_use_case = RequestPasswordResetUseCase(
        SqlAlchemyUnitOfWork, email_sender, get_settings()
    )
    request_use_case.execute(email="admin@vibe-coding-platform.dev")
    token = _extract_token(email_sender.sent[0]["reset_url"])

    reset_use_case = ResetPasswordUseCase(SqlAlchemyUnitOfWork, password_hasher)
    reset_use_case.execute(token=token, new_password="NuevaClave123!")

    with pytest.raises(InvalidOrExpiredTokenError):
        reset_use_case.execute(token=token, new_password="OtraClave123!")


def test_reset_password_rejects_unknown_token(password_hasher):
    reset_use_case = ResetPasswordUseCase(SqlAlchemyUnitOfWork, password_hasher)
    with pytest.raises(InvalidOrExpiredTokenError):
        reset_use_case.execute(token="token-invalido", new_password="NuevaClave123!")


def test_requesting_reset_twice_invalidates_the_previous_token(
    admin_user, password_hasher, email_sender
):
    use_case = RequestPasswordResetUseCase(SqlAlchemyUnitOfWork, email_sender, get_settings())
    use_case.execute(email="admin@vibe-coding-platform.dev")
    first_token = _extract_token(email_sender.sent[0]["reset_url"])

    use_case.execute(email="admin@vibe-coding-platform.dev")

    reset_use_case = ResetPasswordUseCase(SqlAlchemyUnitOfWork, password_hasher)
    with pytest.raises(InvalidOrExpiredTokenError):
        reset_use_case.execute(token=first_token, new_password="NuevaClave123!")
