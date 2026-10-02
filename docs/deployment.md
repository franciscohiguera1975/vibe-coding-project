# Despliegue

La plataforma soporta dos modos, seleccionados por `DEPLOY_MODE` en el `.env` de la
raíz del monorepo (ver `.env.example` y `deploy.yml`): `docker` y `native`. En ambos
casos, PostgreSQL es el único requisito externo — este proyecto no depende de
ningún otro servicio gestionado.

```bash
./scripts/deploy.sh up     # despliega segun DEPLOY_MODE
./scripts/deploy.sh down   # detiene (solo tiene efecto real en modo docker)
```

## Modo Docker (recomendado)

Levanta los tres servicios (`postgres`, `backend`, `frontend`) definidos en
`docker-compose.yml`:

```bash
cp .env.example .env   # ajuste JWT_SECRET, AI_PROVIDER/AI_API_KEY, etc.
make docker-up         # equivalente a: docker compose up -d --build
```

- El backend (`docker/Dockerfile.backend`) corre `alembic upgrade head` al
  arrancar (`docker/backend-entrypoint.sh`) y, si `SEED_ON_START=true` (valor por
  defecto en `docker-compose.yml`), ejecuta el seed idempotente
  (`scripts/seed.py`) — seguro de re-ejecutar porque busca cada entidad por su
  clave natural antes de crearla.
- El frontend (`docker/Dockerfile.frontend`) compila el build estático de Vite
  con `VITE_API_URL` horneado en tiempo de build (variable `build.args` en
  `docker-compose.yml`, porque Vite no lee variables de entorno en runtime) y lo
  sirve con nginx (`docker/nginx.conf.template`).
- `MOODLE_ORIGIN` (variable de entorno del contenedor `frontend`) controla el
  `Content-Security-Policy: frame-ancestors` que permite embeber
  `/practices/{slug}/embed` en un `<iframe>` desde el dominio de Moodle — ver
  `docs/moodle-integration.md`.
- Los archivos subidos (`StorageLocalAdapter`) persisten en el volumen nombrado
  `backend_storage`, independiente del ciclo de vida del contenedor.

```bash
docker compose logs -f backend   # o: make deploy seguido de ./scripts/deploy.sh logs
docker compose down              # detener; agregar -v para borrar tambien los volumenes
```

## Modo nativo

Pensado para un host donde PostgreSQL ya está instalado (o es gestionado por el
departamento de TI) y se prefiere no usar contenedores para la aplicación.

```bash
make install-backend    # crea apps/backend/.venv e instala el paquete editable
make install-frontend   # npm install (workspaces)
make migrate            # alembic upgrade head
make seed                # scripts/seed.py (idempotente)
npm run build:frontend  # genera apps/frontend/dist
```

### Backend: gunicorn + systemd

```ini
# /etc/systemd/system/vibe-coding-backend.service
[Unit]
Description=Vibe Coding Platform - backend
After=network.target postgresql.service

[Service]
Type=simple
User=vibe-coding
WorkingDirectory=/opt/vibe-coding-platform/apps/backend
EnvironmentFile=/opt/vibe-coding-platform/.env
ExecStart=/opt/vibe-coding-platform/apps/backend/.venv/bin/gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker -b 127.0.0.1:3000 --workers 2
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now vibe-coding-backend
```

### Frontend: build estático servido por nginx

El backend solo necesita escuchar en `127.0.0.1` (nginx hace de frente público y
reenvía `/api`):

```nginx
# /etc/nginx/sites-available/vibe-coding-platform
server {
    listen 80;
    server_name practicas.ejemplo.edu;
    root /opt/vibe-coding-platform/apps/frontend/dist;
    index index.html;

    add_header Content-Security-Policy "frame-ancestors 'self' https://moodle.ejemplo.edu" always;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:3000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/vibe-coding-platform /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Nota: a diferencia del modo Docker, aquí `VITE_API_URL` debe apuntar a la misma
URL pública (`https://practicas.ejemplo.edu`) ya que nginx expone `/api` bajo el
mismo origen — evita además configurar CORS en el backend para un origen
distinto.

### Actualizar una instalación nativa existente

```bash
git pull
make install-backend && make install-frontend
make migrate
npm run build:frontend
sudo systemctl restart vibe-coding-backend
sudo systemctl reload nginx
```

## Variables de entorno relevantes para el despliegue

Ver `.env.example` para la lista completa. Las específicas de despliegue:

| Variable | Modo | Efecto |
|---|---|---|
| `DEPLOY_MODE` | ambos | `docker` o `native`; usada por `scripts/deploy.sh` |
| `SEED_ON_START` | docker | si `true`, el backend ejecuta el seed al arrancar el contenedor |
| `MOODLE_ORIGIN` | docker | dominio permitido en `frame-ancestors` para el embebido en Moodle |
| `POSTGRES_PORT` | docker | puerto del host mapeado a Postgres (5433 por defecto: evita chocar con un Postgres nativo del host) |
| `VITE_API_URL` | ambos (build-time) | URL pública de la API, horneada en el bundle del frontend |
