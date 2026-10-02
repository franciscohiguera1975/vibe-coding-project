from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    ConflictError,
    DomainError,
    InvalidCredentialsError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message})


def register_exception_handlers(app: FastAPI) -> None:
    """Manejo centralizado de excepciones (Prompt Maestro §6): los casos de uso lanzan
    excepciones de dominio; aqui se traducen a respuestas HTTP coherentes."""

    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return _error_response(404, str(exc))

    @app.exception_handler(ConflictError)
    async def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
        return _error_response(409, str(exc))

    @app.exception_handler(ValidationError)
    async def handle_validation(request: Request, exc: ValidationError) -> JSONResponse:
        return _error_response(422, str(exc))

    @app.exception_handler(PermissionDeniedError)
    async def handle_permission_denied(
        request: Request, exc: PermissionDeniedError
    ) -> JSONResponse:
        return _error_response(403, str(exc))

    @app.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return _error_response(401, str(exc))

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        return _error_response(400, str(exc))
