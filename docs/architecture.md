# Arquitectura

La plataforma aplica Clean Architecture / Hexagonal Architecture (Ports & Adapters)
tanto en el backend como en el frontend: la lógica de negocio no depende de FastAPI,
SQLAlchemy, PostgreSQL, React ni de ningún proveedor de IA concreto.

## Backend (`apps/backend/app/`)

```
domain/            # entidades (dataclasses puras), value objects, excepciones,
                    # permisos, y los puertos de repositorio (Protocol)
application/       # casos de uso, puertos (AIProvider, StoragePort, EvaluationPort,
                    # UnitOfWork, TokenService, PasswordHasher), servicios (agente, auditoría)
infrastructure/     # implementaciones concretas: modelos SQLAlchemy, repositorios,
                    # adaptadores de IA/almacenamiento/evaluación/seguridad, config
interfaces/http/   # routers FastAPI, schemas Pydantic, dependencias, manejo de excepciones
```

Regla de dependencia: `domain` no importa nada de las otras capas; `application`
solo depende de `domain` y de sus propios puertos; `infrastructure` implementa esos
puertos; `interfaces/http` es el único punto donde FastAPI entra en juego, y los
routers no contienen lógica de negocio — delegan a los casos de uso.

### Unit of Work

`SqlAlchemyUnitOfWork` (`infrastructure/database/unit_of_work.py`) es el único
límite transaccional: agrega todos los repositorios como atributos (`uow.users`,
`uow.practices`, `uow.ai_sessions`, …) y expone `commit()`/`rollback()` vía context
manager. Los casos de uso reciben una fábrica de UoW, nunca una sesión de
SQLAlchemy directamente.

### Puertos y adaptadores clave

| Puerto (`application/ports/`) | Adaptadores (`infrastructure/`) |
|---|---|
| `AIProvider` | `MockAIAdapter` (determinista, sin red), `AnthropicAdapter` |
| `StoragePort` | `LocalStorageAdapter` (funcional), `MinIOAdapter`/`S3Adapter` (stubs documentados) |
| `EvaluationPort` | `RuleBasedEvaluationAdapter` (`numeric_match`, `count_comparison`, `manual`) |
| `PasswordHasher` / `TokenService` | `BcryptPasswordHasher`, `JoseTokenService` |

Ver [`ai.md`](ai.md) y [`ai-agents.md`](ai-agents.md) para el detalle de IA y del
agente tutor.

## Frontend (`apps/frontend/src/`)

```
domain/            # entidades/tipos TS puros (User, PracticeDetail, etc.)
application/       # hooks (React Query), servicios (llaman al puerto HttpClient),
                    # contexto de autenticación
infrastructure/    # ApiClient (implementa HttpClient), almacenamiento de tokens,
                    # raiz de composición (container.ts)
presentation/      # páginas, layouts, componentes, y el registro de tipos de práctica
```

`container.ts` es el único lugar donde la capa de presentación toca un detalle de
infraestructura concreto (la instancia de `ApiClient`); todo lo demás depende solo
de los servicios de `application/`.

### Registro de tipos de práctica

`presentation/practices/registry.ts` mapea `practice.type` (`"software"`,
`"image"`, …) a un componente ejecutor (`SoftwarePracticeRunner`,
`ImagePracticeRunner`), con `UnknownPracticeType` como fallback. Agregar un tipo de
práctica nuevo solo requiere una entrada aquí — ningún otro archivo del flujo de
ejecución de prácticas necesita cambiar (Prompt Maestro §16/§34).

### Transformación de claves HTTP

`ApiClient` convierte automáticamente `camelCase` (TypeScript) ↔ `snake_case`
(API) en cada petición/respuesta, excepto en un conjunto de claves "opacas"
(`content`, `evaluation`, `aiConfiguration`, `embeddingConfiguration`, `metadata`,
`details`, `value`, `payload`): estos campos son JSON libre definido por quien
autora cada práctica, y transformar sus claves internas (p. ej. `speed_kmh`)
rompería el contrato que cada ejecutor espera. Ver `OPAQUE_KEYS` en
`infrastructure/http/api-client.ts`.

## Decisiones no especificadas por el Prompt Maestro (documentadas)

- **Monorepo**: npm workspaces (no pnpm/Turborepo) para `apps/frontend`; el
  backend Python se gestiona aparte con un venv, orquestado por el `Makefile`
  raíz. Se eligió npm workspaces por ser la opción con menor fricción de
  tooling adicional para un proyecto de este tamaño. El scaffold original
  reservaba un workspace `packages/*` para código TS compartido, pero se
  eliminó al no haber surgido ninguna necesidad real de extraer código
  compartido del frontend — se puede reintroducir sin fricción si aparece esa
  necesidad.
- **Proveedor de IA real**: `AnthropicAdapter` (Claude) detrás de `AIProvider`;
  `MockAIAdapter` es el valor por defecto en desarrollo/pruebas.
- **Agente de IA**: orquestador determinista escrito a mano (no un framework tipo
  LangChain ni un loop ReAct libre) — ver [`ai-agents.md`](ai-agents.md) para la
  justificación completa.
- **Conteo de imágenes**: regla explícita por componentes conexas (umbral de
  saturación de color), no un modelo de visión entrenado — coherente con el
  requisito de que la regla de conteo sea explícita y auditable.
- **Almacenamiento**: `LocalStorageAdapter` es el único adaptador operativo sin
  credenciales adicionales; `MinIOAdapter`/`S3Adapter` quedan como stubs con la
  interfaz completa (razonable para un entregable educativo, no para producción
  con object storage real).
- **Base de datos de desarrollo**: PostgreSQL vía Docker Compose incluso cuando
  `DEPLOY_MODE=native` para desarrollo local; el despliegue nativo en producción
  asume PostgreSQL ya instalado en el host (ver
  [`native-deployment.md`](native-deployment.md)).
