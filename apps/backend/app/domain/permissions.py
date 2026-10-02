"""Codigos de permiso. Los del Prompt Maestro §15 son 'de ejemplo' (no exhaustivos);
PRACTICE_PUBLISH y los de rol/configuracion se agregan porque los usan casos de uso
concretos (PublishPractice, AssignRole, AssignPermission, ManageConfiguration)."""

PRACTICE_CREATE = "practice:create"
PRACTICE_READ = "practice:read"
PRACTICE_UPDATE = "practice:update"
PRACTICE_DELETE = "practice:delete"
PRACTICE_PUBLISH = "practice:publish"

USER_CREATE = "user:create"
USER_READ = "user:read"
USER_UPDATE = "user:update"
USER_DELETE = "user:delete"

CONFIGURATION_READ = "configuration:read"
CONFIGURATION_UPDATE = "configuration:update"

ROLE_ASSIGN_PERMISSION = "role:assign_permission"

ALL_PERMISSIONS: dict[str, str] = {
    PRACTICE_CREATE: "Crear practicas",
    PRACTICE_READ: "Leer practicas",
    PRACTICE_UPDATE: "Actualizar practicas",
    PRACTICE_DELETE: "Eliminar practicas",
    PRACTICE_PUBLISH: "Publicar practicas",
    USER_CREATE: "Crear usuarios",
    USER_READ: "Leer usuarios",
    USER_UPDATE: "Actualizar usuarios (incluye asignar roles)",
    USER_DELETE: "Eliminar usuarios",
    CONFIGURATION_READ: "Leer configuraciones",
    CONFIGURATION_UPDATE: "Actualizar configuraciones",
    ROLE_ASSIGN_PERMISSION: "Asignar permisos a un rol",
}

# Roles iniciales sugeridos (Prompt Maestro §15) -> permisos que incluyen.
ROLE_DEFINITIONS: dict[str, list[str]] = {
    "ADMIN": list(ALL_PERMISSIONS.keys()),
    "CONTENT_MANAGER": [
        PRACTICE_CREATE,
        PRACTICE_READ,
        PRACTICE_UPDATE,
        PRACTICE_DELETE,
        PRACTICE_PUBLISH,
    ],
    "TEACHER": [PRACTICE_READ, USER_READ],
    "STUDENT": [PRACTICE_READ],
}
