from fastapi import APIRouter, Depends, status

from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.request_password_reset import RequestPasswordResetUseCase
from app.application.use_cases.auth.reset_password import ResetPasswordUseCase
from app.domain.entities.identity import User
from app.interfaces.http.controllers.auth_controller import tokens_to_response, user_to_public
from app.interfaces.http.dependencies.auth import get_current_user
from app.interfaces.http.dependencies.use_cases import (
    get_login_use_case,
    get_refresh_token_use_case,
    get_request_password_reset_use_case,
    get_reset_password_use_case,
)
from app.interfaces.http.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    TokenResponse,
    UserPublic,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest, use_case: LoginUseCase = Depends(get_login_use_case)
) -> TokenResponse:
    tokens = use_case.execute(email=payload.email, password=payload.password)
    return tokens_to_response(tokens)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest, use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case)
) -> TokenResponse:
    tokens = use_case.execute(refresh_token=payload.refresh_token)
    return tokens_to_response(tokens)


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return user_to_public(current_user)


@router.post("/password-reset/request", status_code=status.HTTP_204_NO_CONTENT)
def request_password_reset(
    payload: PasswordResetRequest,
    use_case: RequestPasswordResetUseCase = Depends(get_request_password_reset_use_case),
) -> None:
    """Siempre responde 204, exista o no el email (evita enumeracion de usuarios)."""
    use_case.execute(email=payload.email)


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(
    payload: PasswordResetConfirm,
    use_case: ResetPasswordUseCase = Depends(get_reset_password_use_case),
) -> None:
    use_case.execute(token=payload.token, new_password=payload.new_password)
