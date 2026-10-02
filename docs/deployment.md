# Despliegue

La plataforma soporta dos modos, seleccionados por `DEPLOY_MODE` en el `.env` de la
raíz del monorepo (ver `.env.example` y `deploy.yml`): `docker` y `native`. En ambos
casos, PostgreSQL es el único requisito externo — el proyecto no depende de ningún
otro servicio gestionado.

```bash
./scripts/deploy.sh up     # despliega segun DEPLOY_MODE
./scripts/deploy.sh down   # detiene (solo tiene efecto real en modo docker)
```

- **`docker`** (recomendado para evaluación rápida y para el despliegue
  institucional por defecto): ver [`docker.md`](docker.md).
- **`native`** (cuando PostgreSQL/nginx ya son gestionados por el host): ver
  [`native-deployment.md`](native-deployment.md).

## Variables de entorno relevantes para el despliegue

Ver [`configuration.md`](configuration.md) para la lista completa. Las
específicas de despliegue:

| Variable | Modo | Efecto |
|---|---|---|
| `DEPLOY_MODE` | ambos | `docker` o `native`; usada por `scripts/deploy.sh` |
| `SEED_ON_START` | docker | si `true`, el backend ejecuta el seed al arrancar el contenedor |
| `MOODLE_ORIGIN` | docker | dominio permitido en `frame-ancestors` para el embebido en Moodle |
| `POSTGRES_PORT` | docker | puerto del host mapeado a Postgres (5433 por defecto: evita chocar con un Postgres nativo del host) |
| `VITE_API_URL` | ambos (build-time) | URL pública de la API, horneada en el bundle del frontend |

## Qué modo elegir

`docker` es la ruta mas simple de reproducir y la que se verificó end-to-end
(`docker compose build && up`, API + SPA + ruta de embebido + cabecera CSP, ver
`docker.md`). `native` tiene sentido cuando el host ya tiene PostgreSQL y nginx
administrados (por ejemplo, un servidor universitario existente) y se prefiere no
introducir un runtime de contenedores adicional.
