# Configuración (variables de entorno)

Todas las variables viven en un único `.env` en la raíz del monorepo (copiado de
`.env.example`), leído tanto por el backend (`pydantic-settings`, ver
`apps/backend/app/infrastructure/config.py`) como por el frontend (Vite, con
`envDir` apuntando a la raíz — ver `apps/frontend/vite.config.ts`). Nunca commitear
un `.env` con valores reales.

| Variable | Default | Descripción |
|---|---|---|
| `NODE_ENV` | `development` | Entorno Node (frontend) |
| `DEPLOY_MODE` | `native` | `docker` o `native` — ver [`deployment.md`](deployment.md) |
| `SEED_ON_START` | `true` | Solo Docker: ejecuta el seed al arrancar el contenedor backend |
| `MOODLE_ORIGIN` | _(vacío)_ | Solo Docker: dominio permitido en `frame-ancestors` para embebido en Moodle |
| `BACKEND_PORT` | `3000` | Puerto del backend |
| `BACKEND_URL` | `http://localhost:3000` | URL pública del backend (usada para construir URLs de archivos) |
| `DATABASE_URL` | `postgresql://vibe_coding:vibe_coding@localhost:5433/vibe_coding_dev` | Cadena de conexión a PostgreSQL; `postgresql://` se normaliza automáticamente a `postgresql+psycopg://` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `vibe_coding` / `vibe_coding` / `vibe_coding_dev` | Credenciales del servicio `postgres` en `docker-compose.yml` |
| `POSTGRES_PORT` | `5433` | Puerto del host mapeado a Postgres (5433, no 5432, para no chocar con un PostgreSQL nativo del host) |
| `JWT_SECRET` | `change-me-in-dev` | Clave de firma de los JWT — **cambiar en cualquier despliegue real** |
| `JWT_ACCESS_EXPIRES_IN` / `JWT_REFRESH_EXPIRES_IN` | `15m` / `7d` | Vigencia de access/refresh tokens (formato `Ns`/`Nm`/`Nh`/`Nd`) |
| `FRONTEND_PORT` | `5173` | Puerto del frontend |
| `FRONTEND_URL` | `http://localhost:5173` | Origen del frontend, usado como `CORS_ALLOWED_ORIGINS` por defecto |
| `VITE_API_URL` | `http://localhost:3000` | URL de la API consumida por el frontend — horneada en el bundle en tiempo de build |
| `AI_PROVIDER` | `mock` | `mock` (sin red, determinista) o `anthropic` |
| `AI_API_KEY` | _(vacío)_ | API key de Anthropic; requerida solo si `AI_PROVIDER=anthropic` |
| `STORAGE_PROVIDER` | `local` | `local`, `minio` o `s3` — ver [`ai.md`](ai.md) §Imágenes y `architecture.md` |
| `STORAGE_LOCAL_PATH` | `./storage/uploads` | Carpeta de archivos subidos (adaptador local) |
| `STORAGE_MINIO_*` / `STORAGE_S3_BUCKET` | _(vacío)_ | Configuración de los adaptadores MinIO/S3 (stubs, ver `architecture.md`) |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Lista separada por comas de orígenes permitidos |

Campos adicionales, configurables via env pero no listados en `.env.example` por
no necesitar ajuste habitual (ver `Settings` en `config.py` para sus nombres de
variable): `AI_MODEL` (`claude-sonnet-5`), `AI_AGENT_MAX_ITERATIONS` (8),
`AI_AGENT_MAX_TOKENS` (4000), `STORAGE_MAX_UPLOAD_MB` (10), `JWT_ALGORITHM`
(`HS256`).
