#!/bin/sh
# Despacha el despliegue segun DEPLOY_MODE (ver deploy.yml y docs/deployment.md).
# Uso: ./scripts/deploy.sh [up|down|logs]
set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(dirname "$SCRIPT_DIR")
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

MODE=${DEPLOY_MODE:-native}
ACTION=${1:-up}

case "$MODE" in
  docker)
    case "$ACTION" in
      up) exec docker compose up -d --build ;;
      down) exec docker compose down ;;
      logs) exec docker compose logs -f ;;
      *) echo "Accion desconocida: $ACTION (use up|down|logs)" >&2; exit 1 ;;
    esac
    ;;
  native)
    case "$ACTION" in
      up)
        echo "DEPLOY_MODE=native: ejecutando los pasos de deploy.yml#modes.native.steps"
        make install-backend
        make install-frontend
        make migrate
        make seed
        npm run build:frontend
        echo "Build lista. Inicie el backend (gunicorn) y sirva apps/frontend/dist con nginx;"
        echo "ver docs/deployment.md para los comandos y unidades systemd de ejemplo."
        ;;
      down)
        echo "DEPLOY_MODE=native no administra procesos; deténga sus propios servicios systemd/nginx." >&2
        exit 1
        ;;
      *) echo "Accion desconocida: $ACTION (use up|down)" >&2; exit 1 ;;
    esac
    ;;
  *)
    echo "DEPLOY_MODE invalido: $MODE (use docker|native)" >&2
    exit 1
    ;;
esac
