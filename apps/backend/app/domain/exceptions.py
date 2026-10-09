"""Excepciones de dominio. No dependen de FastAPI ni de HTTP: el mapeo a codigos de
estado ocurre en interfaces/http (manejo centralizado de excepciones, Prompt Maestro §6)."""


class DomainError(Exception):
    """Base de todas las excepciones de negocio."""


class NotFoundError(DomainError):
    def __init__(self, entity: str, identifier: str) -> None:
        self.entity = entity
        self.identifier = identifier
        super().__init__(f"{entity} '{identifier}' no encontrado")


class ConflictError(DomainError):
    """Un recurso ya existe o el estado actual impide la operacion (p.ej. email duplicado)."""


class ValidationError(DomainError):
    """Los datos de entrada no cumplen una regla de negocio (no confundir con validacion
    de esquema HTTP, que maneja Pydantic en interfaces/http/schemas)."""


class PermissionDeniedError(DomainError):
    def __init__(self, permission: str) -> None:
        self.permission = permission
        super().__init__(f"Permiso requerido: {permission}")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("Credenciales invalidas")


class InvalidOrExpiredTokenError(DomainError):
    def __init__(self) -> None:
        super().__init__("El enlace de restablecimiento es invalido o ha expirado")


class AgentLimitExceededError(DomainError):
    """El AI Tutor Agent alcanzo su limite de iteraciones/tokens (Prompt Maestro §11)."""


class ExternalServiceError(DomainError):
    """Un proveedor externo (p.ej. ElevenLabs) respondio con un error. Los adaptadores
    de infrastructure traducen aqui cualquier excepcion de su cliente HTTP para que
    la capa de aplicacion/interfaces nunca dependa de una libreria externa concreta."""

    def __init__(self, service: str, detail: str) -> None:
        self.service = service
        self.detail = detail
        super().__init__(f"Error del servicio externo '{service}': {detail}")
