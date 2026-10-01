# AGENTS.md

Convenciones para agentes de IA (y humanos) que trabajen en este monorepo.

## 1. Arquitectura

Clean Architecture + Hexagonal en `apps/backend` y `apps/frontend`. La lógica de negocio
(`domain/`, `application/`) no debe importar FastAPI, SQLAlchemy, React ni un proveedor de IA
concreto. Ver `docs/architecture.md`.

## 2. Monorepo

- `npm install` en la raíz instala `apps/frontend` y `packages/*` (npm workspaces).
- El backend Python se gestiona aparte: `make install-backend` crea el venv en
  `apps/backend/.venv`.
- Usa los targets de `Makefile` (`make dev-backend`, `make dev-frontend`, `make test`, `make seed`)
  en vez de invocar las herramientas directamente, para mantener consistencia entre entornos.

## 3. Prácticas

Agregar una práctica nueva de un tipo existente (`software`, `image`, …) es un registro en
`database/seeds` + una fila en la tabla `practices`, **no** un cambio de código. Un tipo de
práctica genuinamente nuevo requiere una entrada en el registro de tipos del frontend
(`apps/frontend/src/presentation/practices/registry.ts`) y su esquema compartido en
`packages/types`.

## 4. IA

Todo acceso a un proveedor de IA pasa por el puerto `AIProvider`
(`apps/backend/app/application/ports`). En desarrollo y pruebas usa `AI_PROVIDER=mock`
(`MockAIAdapter`) — las pruebas nunca deben requerir una clave de API real.

## 5. Pruebas

Antes de dar por cerrada una fase: `make test-backend` (pytest) y, si aplica,
`make test-frontend`. Las migraciones (`make migrate`) y los seeds (`make seed`) deben poder
re-ejecutarse sin duplicar datos.

## 6. Secretos

Nunca commitear `.env` con valores reales. Usa `.env.example` como referencia; las claves de IA,
JWT y base de datos de producción se inyectan por variable de entorno en el entorno de
despliegue, nunca en el repositorio.
