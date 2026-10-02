# Vibe Coding Platform

Plataforma web educativa para la enseñanza práctica de desarrollo de software y
manejo de imágenes con apoyo de Inteligencia Artificial, orientada a un curso de
Vibe Coding: prácticas interactivas, reutilizables y escalables, con IA
desacoplada y un primer agente de IA tutor.

## Características

- **Catálogo de prácticas** público, filtrable por categoría, dificultad,
  tecnología y tipo, con área privada de administración (RBAC).
- **Prácticas de software** con simulación interactiva en el navegador
  (predecir → ajustar → ejecutar → observar → explicar) y ejercicios de
  depuración/evaluación de código.
- **Prácticas de manejo de imágenes** con una regla de conteo explícita y
  determinista (no un modelo entrenado), comparación contra referencia humana,
  y diagnóstico de errores.
- **IA desacoplada**: puerto `AIProvider` con un adaptador mock (determinista,
  sin red) y uno real (Anthropic Claude), intercambiables por variable de
  entorno.
- **AI Tutor Agent**: orquestador determinista (no un framework de agentes)
  con herramientas controladas, límites de iteraciones/tokens y trazabilidad
  completa de cada llamada.
- **Embebido en Moodle** vía iframe (`/practices/{slug}/embed`), sin depender
  del layout del portal.
- **RBAC** completo (usuarios, roles, permisos, auditoría) y **Clean/Hexagonal
  Architecture** en backend y frontend.
- Despliegue con **Docker** o **nativo** (`DEPLOY_MODE`), con los mismos
  comandos de alto nivel.

## Arquitectura

Clean Architecture / Hexagonal (Ports & Adapters) en ambos lados: el dominio no
depende de FastAPI, SQLAlchemy, PostgreSQL, React ni de ningún proveedor de IA
concreto. Ver [`docs/architecture.md`](docs/architecture.md) para el detalle
completo (capas, puertos/adaptadores y las decisiones de diseño no
especificadas por el encargo, documentadas allí).

## Stack tecnológico

| | |
|---|---|
| Backend | Python · FastAPI · SQLAlchemy 2.x · Alembic · PostgreSQL |
| Frontend | React · TypeScript · Vite · Tailwind CSS · React Router · React Query |
| Auth | JWT (access + refresh) · bcrypt |
| IA | Anthropic Claude (adaptador real) · adaptador mock determinista |
| Infraestructura | Docker / despliegue nativo (gunicorn + nginx) |

## Requisitos

Python ≥ 3.11 · Node.js ≥ 20 · PostgreSQL (local, Docker, o remoto).

## Instalación rápida

```bash
git clone <url-del-repositorio>
cd vibe-coding-platform
cp .env.example .env

make install-backend install-frontend
make migrate
make seed

make dev-backend    # http://localhost:3000/docs
make dev-frontend   # http://localhost:5173
```

Detalle completo en [`docs/installation.md`](docs/installation.md).

## Docker

```bash
make docker-up   # docker compose up -d --build: postgres + backend + frontend
```

Ver [`docs/docker.md`](docs/docker.md).

## Despliegue nativo

gunicorn + systemd para el backend, build estático de Vite servido por nginx.
Ver [`docs/native-deployment.md`](docs/native-deployment.md). Ambos modos se
seleccionan con `DEPLOY_MODE` — ver [`docs/deployment.md`](docs/deployment.md).

## Variables de entorno

Un único `.env` en la raíz (ver `.env.example`), leído tanto por el backend como
por el frontend. Referencia completa en
[`docs/configuration.md`](docs/configuration.md).

## Migraciones y seeds

```bash
make migrate                      # alembic upgrade head
make migration m="descripcion"    # alembic revision --autogenerate
make seed                          # scripts/seed.py (idempotente)
```

Ver [`docs/database.md`](docs/database.md).

## Ejecución y prácticas

Flujo de una práctica: seleccionar → leer objetivos/instrucciones → iniciar →
realizar la actividad → enviar resultado → evaluación automática/manual →
pista o feedback de IA opcional → progreso registrado. El modelo de prácticas
es una entidad configurable (no código por práctica) — ver
[`docs/practices.md`](docs/practices.md) para el modelo de datos y las 4
prácticas iniciales, y [`docs/api.md`](docs/api.md) para los endpoints.

## IA y agente

[`docs/ai.md`](docs/ai.md) (puerto `AIProvider`, adaptadores, manejo de
imágenes, evaluación) y [`docs/ai-agents.md`](docs/ai-agents.md) (diseño del AI
Tutor Agent, herramientas, límites, trazabilidad).

## Moodle

Cada práctica se puede embeber en un curso de Moodle vía `<iframe>` sin la
navegación del portal — ver [`docs/moodle-integration.md`](docs/moodle-integration.md).

## Testing

```bash
make test             # backend (pytest) + frontend (vitest)
make test-backend
make test-frontend
```

Ver [`docs/testing.md`](docs/testing.md) (incluye una nota importante: la suite
de backend vacía la base de datos de desarrollo en cada corrida).

## Documentación completa

Todo en [`docs/`](docs/): [`architecture.md`](docs/architecture.md) ·
[`installation.md`](docs/installation.md) ·
[`configuration.md`](docs/configuration.md) ·
[`deployment.md`](docs/deployment.md) · [`docker.md`](docs/docker.md) ·
[`native-deployment.md`](docs/native-deployment.md) ·
[`database.md`](docs/database.md) · [`api.md`](docs/api.md) ·
[`authentication.md`](docs/authentication.md) ·
[`authorization.md`](docs/authorization.md) · [`ai.md`](docs/ai.md) ·
[`ai-agents.md`](docs/ai-agents.md) · [`practices.md`](docs/practices.md) ·
[`moodle-integration.md`](docs/moodle-integration.md) ·
[`development.md`](docs/development.md) · [`testing.md`](docs/testing.md) ·
[`troubleshooting.md`](docs/troubleshooting.md).
