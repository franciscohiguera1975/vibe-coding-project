# Base de datos

PostgreSQL, modelado con SQLAlchemy 2.x (estilo declarativo) y migrado con
Alembic. SQLAlchemy vive exclusivamente en `infrastructure/database/` — el
dominio no conoce la base de datos (ver [`architecture.md`](architecture.md)).

## Entidades

| Tabla | Modelo (`infrastructure/database/models/`) | Propósito |
|---|---|---|
| `users` | `UserModel` (`identity.py`) | Cuentas; relación muchos-a-muchos con `roles` vía `user_roles` |
| `roles` | `RoleModel` | ADMIN, CONTENT_MANAGER, TEACHER, STUDENT (seedados) |
| `permissions` | `PermissionModel` | Catálogo de códigos de permiso (ver [`authorization.md`](authorization.md)) |
| `user_roles` | tabla de asociación (`identity.py`) | — |
| `role_permissions` | tabla de asociación (`identity.py`) | — |
| `practices` | `PracticeModel` (`practice.py`) | Metadatos de cada práctica (slug, tipo, dificultad, estado, …) |
| `practice_contents` | `PracticeContentModel` | `content`/`evaluation`/`ai_configuration`/`embedding_configuration`/`metadata` (JSONB) |
| `practice_categories` | `PracticeCategoryModel` (`catalog.py`) | Categorías del catálogo |
| `practice_tags` | `PracticeTagModel` | Etiquetas; `practice_practice_tags` es la tabla de asociación |
| `student_practice_attempts` | `StudentPracticeAttemptModel` (`progress.py`) | Un intento de un estudiante sobre una práctica |
| `practice_submissions` | `PracticeSubmissionModel` | Payload enviado por el estudiante para un intento |
| `practice_evaluations` | `PracticeEvaluationModel` | Resultado (score/passed/feedback) de una submission |
| `student_progress` | `StudentProgressModel` | Agregado de progreso por estudiante/práctica |
| `ai_sessions` | `AISessionModel` (`ai.py`) | Una ejecución del AI Tutor Agent |
| `ai_messages` | `AIMessageModel` | Mensajes usuario/asistente de una sesión |
| `ai_tool_calls` | `AIToolCallModel` | Cada llamada a herramienta del agente (permitida/denegada/error), para trazabilidad |
| `configurations` | `ConfigurationModel` (`system.py`) | Pares clave/valor administrables desde el panel |
| `audit_logs` | `AuditLogModel` | Registro de acciones administrativas (ver `application/services/audit.py`) |

16 modelos en total, agregados en `models/__init__.py` para que Alembic y
SQLAlchemy resuelvan todas las relaciones entre módulos.

## Migraciones

```bash
make migrate                      # alembic upgrade head
make migration m="descripcion"    # alembic revision --autogenerate -m "..."
```

La migración inicial (`alembic/versions/7930dbac353a_initial_schema.py`) incluye
`downgrade()` explícito para los 8 tipos ENUM de Postgres usados (difficulty,
status, attempt status, etc.): Postgres no los elimina automáticamente al
eliminar las tablas que los usan, así que cada uno se dropea explícitamente
(`sa.Enum(name=...).drop(bind, checkfirst=True)`) para que el ciclo
upgrade/downgrade sea idempotente.

## Seeds

```bash
make seed   # apps/backend/scripts/seed.py
```

Idempotente: cada entidad se busca por su clave natural (email, nombre de rol,
código de permiso, slug de práctica) antes de crearse, así que puede ejecutarse
repetidamente sin duplicar datos ni fallar sobre una base ya seedada. Crea:
roles y permisos (sincronizando también los permisos de roles ya existentes, no
solo al crearlos), el usuario administrador de desarrollo, las categorías del
catálogo, un conjunto de configuraciones, y las 4 prácticas iniciales
(`database/seeds/practices_data.py`).

## Unit of Work

Todo acceso a datos pasa por `SqlAlchemyUnitOfWork` (`infrastructure/database/
unit_of_work.py`): agrega cada repositorio como atributo y es el único límite
transaccional — los casos de uso nunca abren una sesión de SQLAlchemy por su
cuenta.
