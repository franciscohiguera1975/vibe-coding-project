from app.application.dto.auth_dto import AuthTokens
from app.domain.entities.identity import User
from app.interfaces.http.schemas.auth import TokenResponse, UserPublic


def user_to_public(user: User) -> UserPublic:
    permission_codes = sorted({p.code for role in user.roles for p in role.permissions})
    return UserPublic(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=[r.name for r in user.roles],
        permissions=permission_codes,
    )


def tokens_to_response(tokens: AuthTokens) -> TokenResponse:
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        user=user_to_public(tokens.user),
    )
