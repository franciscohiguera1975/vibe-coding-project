# Instalación (desarrollo local, sin Docker)

Para levantar todo con Docker en su lugar, ver [`docker.md`](docker.md).

## Prerrequisitos

- Python ≥ 3.11
- Node.js ≥ 20 (ver `.nvmrc`)
- PostgreSQL accesible (local, vía Docker, o remoto) — la forma más simple es:
  ```bash
  docker compose up -d postgres
  ```

## Pasos

```bash
git clone <url-del-repositorio>
cd vibe-coding-platform
cp .env.example .env   # revise DATABASE_URL, JWT_SECRET, etc.

make install-backend    # crea apps/backend/.venv e instala el paquete editable (+dev)
make install-frontend   # npm install (workspaces)

make migrate            # alembic upgrade head
make seed                # scripts/seed.py (idempotente)
```

## Arrancar en desarrollo

```bash
make dev-backend     # uvicorn --reload en $BACKEND_PORT (3000 por defecto)
make dev-frontend     # vite dev en $FRONTEND_PORT (5173 por defecto)
```

- Backend: http://localhost:3000/docs (Swagger/OpenAPI autogenerado)
- Frontend: http://localhost:5173

## Credenciales del administrador de desarrollo

El seed crea un usuario ADMIN si no existe uno con ese correo:

```
SEED_ADMIN_EMAIL=admin@vibecoding-platform.dev   (valor por defecto)
SEED_ADMIN_PASSWORD=ChangeMe123!                  (valor por defecto)
```

Defina `SEED_ADMIN_EMAIL`/`SEED_ADMIN_PASSWORD` en `.env` antes de ejecutar
`make seed` para usar credenciales propias. **Cambie estas credenciales antes de
cualquier despliegue real** — son solo para desarrollo/evaluación local.

## Verificar la instalación

```bash
make test               # backend (pytest) + frontend (vitest)
curl http://localhost:3000/health   # {"status": "ok"}
```

Si algo falla, ver [`troubleshooting.md`](troubleshooting.md) para los problemas
más comunes (puerto de Postgres ocupado, dependencias nativas de Pillow, etc.).
