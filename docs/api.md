# API

API REST documentada automáticamente vía OpenAPI/Swagger en `/docs` (y el schema
crudo en `/openapi.json`) mientras el backend corre. Todas las rutas van bajo el
prefijo `/api`.

Autenticación: header `Authorization: Bearer <access_token>` (ver
[`authentication.md`](authentication.md)). Autorización: cada endpoint protegido
declara el permiso que requiere vía `require_permission(...)` (ver
[`authorization.md`](authorization.md)).

## Salud

| Método | Ruta | Auth |
|---|---|---|
| GET | `/api/health` | pública |

## Autenticación (`routers/auth.py`)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/auth/login` | pública | `{email, password}` → tokens + usuario |
| POST | `/api/auth/refresh` | pública | `{refresh_token}` → nuevos tokens |
| GET | `/api/auth/me` | Bearer | usuario autenticado actual |

## Usuarios y roles (`routers/users.py`, `routers/roles.py`)

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/users` | `user:read` |
| POST | `/api/users` | `user:create` |
| POST | `/api/users/{user_id}/roles` | `user:update` |
| GET | `/api/roles` | `user:read` |
| POST | `/api/roles/{role_name}/permissions` | `role:assign_permission` |

## Prácticas (`routers/practices.py`)

| Método | Ruta | Auth/Permiso | Descripción |
|---|---|---|---|
| GET | `/api/practices` | opcional* | catálogo paginado, filtros: categoría, dificultad, tecnología, tipo, estado, búsqueda |
| GET | `/api/practices/{slug}` | opcional* | detalle de una práctica |
| POST | `/api/practices` | `practice:create` | crear práctica |
| PATCH | `/api/practices/{practice_id}` | `practice:update` | actualizar práctica |
| POST | `/api/practices/{practice_id}/publish` | `practice:publish` | publicar (draft → published) |
| POST | `/api/practices/{slug}/start` | Bearer | inicia un intento para el usuario autenticado |
| POST | `/api/practices/attempts/submit` | Bearer | `{attempt_id, payload}` → envía una submission |
| POST | `/api/practices/submissions/{submission_id}/evaluate` | Bearer | evalúa una submission (`RuleBasedEvaluationAdapter`) |

\* sin sesión se listan solo las prácticas publicadas; con `practice:read` también
se ven los borradores.

## Catálogo (`routers/catalog.py`)

| Método | Ruta | Permiso |
|---|---|---|
| GET / POST | `/api/practice-categories` | lectura pública / `practice:create` |
| GET / POST | `/api/practice-tags` | lectura pública / `practice:create` |

## Configuraciones y auditoría (`routers/configurations.py`, `routers/audit.py`)

| Método | Ruta | Permiso |
|---|---|---|
| GET | `/api/configurations` | `configuration:read` |
| PUT | `/api/configurations/{key}` | `configuration:update` |
| GET | `/api/audit` | `audit:read` |

## IA (`routers/ai.py`, `routers/agent.py`) — ver [`ai.md`](ai.md) / [`ai-agents.md`](ai-agents.md)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/ai/hint` | Bearer | pista contextual para una práctica |
| POST | `/api/ai/feedback` | Bearer | retroalimentación sobre una submission evaluada |
| POST | `/api/agent/run` | Bearer | ejecuta el AI Tutor Agent (ver `ai-agents.md`) |

## Imágenes y almacenamiento (`routers/images.py`, `routers/storage.py`) — ver [`ai.md`](ai.md)

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/images/analyze` | Bearer | multipart `{practice_slug, file}` → conteo + advertencias |
| GET | `/api/storage/{key}` | pública | sirve un archivo subido (usado por `get_url` de `StoragePort`) |

## Errores

Las excepciones de dominio se mapean centralizadamente
(`interfaces/http/exception_handlers.py`) a códigos HTTP coherentes:
`NotFoundError`→404, `ConflictError`→409, `ValidationError`→422,
`PermissionDeniedError`→403, `InvalidCredentialsError`→401,
`AgentLimitExceededError`→429, y cualquier otro `DomainError`→400. El cuerpo de
error sigue el formato estándar de FastAPI (`{"detail": "..."}`).
