# Despliegue con Docker

Levanta los tres servicios (`postgres`, `backend`, `frontend`) definidos en
`docker-compose.yml`.

```bash
cp .env.example .env   # ajuste JWT_SECRET, AI_PROVIDER/AI_API_KEY, MOODLE_ORIGIN, etc.
make docker-up         # equivalente a: docker compose up -d --build
```

## Qué hace cada servicio

- **`postgres`** (`postgres:16-alpine`): persiste en el volumen `postgres_data`;
  expuesto en el host en `POSTGRES_PORT` (5433 por defecto, para no chocar con un
  PostgreSQL nativo del host que normalmente usa 5432).
- **`backend`** (`docker/Dockerfile.backend`): imagen Python 3.12 con el paquete
  del backend instalado en modo editable. Su entrypoint
  (`docker/backend-entrypoint.sh`):
  1. espera a que PostgreSQL acepte conexiones;
  2. ejecuta `alembic upgrade head`;
  3. si `SEED_ON_START=true` (valor por defecto en `docker-compose.yml`), ejecuta
     el seed idempotente (`scripts/seed.py` — seguro de re-ejecutar porque busca
     cada entidad por su clave natural antes de crearla);
  4. arranca `gunicorn` con workers `uvicorn.workers.UvicornWorker`.

  La jerarquía `apps/backend/` + `database/` se preserva dentro de la imagen (en
  vez de aplanarla) porque `scripts/seed.py` localiza `database/seeds` subiendo
  dos niveles desde su propio archivo, igual que en desarrollo local.
- **`frontend`** (`docker/Dockerfile.frontend`): build de dos etapas — compila el
  bundle estático de Vite (`VITE_API_URL` se pasa como `build.args`, porque Vite
  lo hornea en el bundle en tiempo de build y no lo lee en runtime) y lo sirve con
  nginx. `docker/nginx.conf.template` se procesa con el mecanismo de plantillas
  oficial de la imagen `nginx:alpine` (`envsubst` sobre
  `/etc/nginx/templates/*.template`), así `MOODLE_ORIGIN` (variable de entorno del
  contenedor `frontend`) puede ajustar la cabecera
  `Content-Security-Policy: frame-ancestors` sin reconstruir la imagen — ver
  [`moodle-integration.md`](moodle-integration.md).

Los archivos subidos (`LocalStorageAdapter`) persisten en el volumen nombrado
`backend_storage`, independiente del ciclo de vida del contenedor.

## Operación

```bash
docker compose logs -f backend   # o: make deploy seguido de ./scripts/deploy.sh logs
docker compose ps
docker compose down              # detener; agregar -v para borrar tambien los volumenes
```

## Verificado

Este flujo se probó de punta a punta con `docker compose build && up`:
`GET /api/practices/{slug}` responde `200` a través del contenedor `backend`, la
SPA se sirve y resuelve rutas internas (`try_files ... /index.html`) a través del
contenedor `frontend`, `/practices/{slug}/embed` carga sin la navegación pública,
y la cabecera `Content-Security-Policy: frame-ancestors` aparece con el valor
esperado.

### Nota sobre `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`

`docker-compose.yml` usa `env_file: .env` (opcional) para el servicio `backend`
en vez de listar estas dos variables con un valor por defecto vacío. Fijarlas
explícitamente a `${SEED_ADMIN_EMAIL:-}` las pisaría con una cadena vacía cuando
no están definidas en `.env` — distinto de no fijarlas, que es lo que permite que
`scripts/seed.py` aplique su propio valor por defecto
(`admin@vibecoding-platform.dev` / `ChangeMe123!`). Si quiere un admin distinto,
defínalas en `.env` y `env_file` las pasará tal cual.
