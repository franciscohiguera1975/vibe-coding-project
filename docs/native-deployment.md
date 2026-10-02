# Despliegue nativo (sin Docker)

Pensado para un host donde PostgreSQL ya está instalado (o es gestionado por el
departamento de TI) y se prefiere no usar contenedores para la aplicación.

```bash
make install-backend    # crea apps/backend/.venv e instala el paquete editable
make install-frontend   # npm install (workspaces)
make migrate            # alembic upgrade head
make seed                # scripts/seed.py (idempotente)
npm run build:frontend  # genera apps/frontend/dist
```

## Backend: gunicorn + systemd

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

## Frontend: build estático servido por nginx

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

## PostgreSQL

El proyecto asume un PostgreSQL ya instalado y accesible (local o gestionado por
TI); `DATABASE_URL` en `.env` apunta a él. No se incluye automatización de
instalación de PostgreSQL en sí — está fuera del alcance de este modo, que
deliberadamente delega esa pieza a la infraestructura existente del host.

## Actualizar una instalación nativa existente

```bash
git pull
make install-backend && make install-frontend
make migrate
npm run build:frontend
sudo systemctl restart vibe-coding-backend
sudo systemctl reload nginx
```
