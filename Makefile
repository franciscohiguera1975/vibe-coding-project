.PHONY: help dev-backend dev-frontend install-backend install-frontend migrate seed test test-backend test-frontend lint lint-backend lint-frontend format docker-up docker-down

BACKEND_DIR = apps/backend
VENV = $(BACKEND_DIR)/.venv
PY = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help:
	@echo "Targets: install-backend install-frontend dev-backend dev-frontend migrate seed test lint format docker-up docker-down"

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

install-backend: $(VENV)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -e "$(BACKEND_DIR)[dev]"

install-frontend:
	npm install

dev-backend:
	cd $(BACKEND_DIR) && .venv/bin/uvicorn app.main:app --reload --port $${BACKEND_PORT:-3000}

dev-frontend:
	npm run dev:frontend

migrate:
	cd $(BACKEND_DIR) && .venv/bin/alembic upgrade head

migration:
	cd $(BACKEND_DIR) && .venv/bin/alembic revision --autogenerate -m "$(m)"

seed:
	cd $(BACKEND_DIR) && .venv/bin/python scripts/seed.py

test-backend:
	cd $(BACKEND_DIR) && .venv/bin/pytest

test-frontend:
	npm run test:frontend

test: test-backend test-frontend

lint-backend:
	cd $(BACKEND_DIR) && .venv/bin/ruff check . && .venv/bin/black --check .

lint-frontend:
	npm run lint:frontend

lint: lint-backend lint-frontend

format:
	cd $(BACKEND_DIR) && .venv/bin/ruff check --fix . && .venv/bin/black .

docker-up:
	docker compose up -d

docker-down:
	docker compose down
