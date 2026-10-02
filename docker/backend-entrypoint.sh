#!/bin/sh
set -e

echo "Esperando a PostgreSQL..."
until python -c "
import sys, time
import psycopg
try:
    psycopg.connect('${DATABASE_URL}', connect_timeout=3).close()
except Exception as exc:
    print(exc)
    sys.exit(1)
" 2>/dev/null; do
  sleep 1
done

echo "Aplicando migraciones..."
alembic upgrade head

if [ "${SEED_ON_START:-false}" = "true" ]; then
  echo "Ejecutando seed idempotente..."
  python scripts/seed.py
fi

exec "$@"
