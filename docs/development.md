# Desarrollo

## Estructura del monorepo

```
apps/backend/     # FastAPI, Clean/Hexagonal, Alembic, pytest
apps/frontend/    # React + TS + Vite + Tailwind + React Router
packages/*/        # reservado para código TS compartido (hoy sin contenido —
                    # el frontend no ha necesitado extraer nada aún)
database/seeds/   # datos de seed (roles, permisos, categorías, prácticas)
docker/           # Dockerfiles + nginx.conf.template
docs/             # esta documentación
scripts/          # deploy.sh
```

Ver [`architecture.md`](architecture.md) para la estructura interna de
`apps/backend/app/` y `apps/frontend/src/`.

## Comandos (`Makefile`)

```bash
make install-backend / install-frontend   # instalar dependencias
make dev-backend / dev-frontend           # levantar en modo desarrollo
make migrate / migration m="..."          # Alembic
make seed                                 # scripts/seed.py (idempotente)
make test / test-backend / test-frontend  # pytest / vitest
make lint / lint-backend / lint-frontend  # ruff+black / eslint
make format                                # ruff --fix + black
make docker-up / docker-down               # docker compose
make deploy / deploy-down                  # scripts/deploy.sh (según DEPLOY_MODE)
```

## Convenciones de código

- **Backend**: Python moderno con type hints en toda firma pública, `ruff` +
  `black` (`make lint-backend` / `make format`), principios SOLID y Clean Code,
  separación estricta de capas (ver `architecture.md`) — un router nunca
  contiene lógica de negocio, un caso de uso nunca importa SQLAlchemy
  directamente.
- **Frontend**: TypeScript estricto, ESLint + Prettier, componentes
  reutilizables, sin lógica de negocio compleja embebida en JSX (delegada a
  hooks/servicios de `application/`).
- Sin secretos hardcodeados; toda configuración vía variables de entorno (ver
  [`configuration.md`](configuration.md)).

## Flujos comunes

- **Agregar un endpoint**: schema Pydantic → caso de uso en `application/
  use_cases/` → repositorio/puerto si hace falta uno nuevo → router (delgado,
  solo orquesta) → dependencia de permiso si corresponde.
- **Agregar un tipo de práctica**: ver [`practices.md`](practices.md) §Agregar un
  tipo de práctica nuevo.
- **Agregar una herramienta al agente**: función en
  `application/services/agent/tools.py` + entrada en `TOOL_REGISTRY` — ver
  [`ai-agents.md`](ai-agents.md).

## CI/CD (pipeline sugerido, no implementado en este repositorio)

`Install → Lint → Test → Build → Deploy`, contemplando ambos modos de despliegue
mediante `DEPLOY_MODE` y ejecutando migraciones de forma controlada (nunca
exponer secretos en los logs del pipeline).
