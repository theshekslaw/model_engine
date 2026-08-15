UV ?= uv

.PHONY: install sync dev lint fmt typecheck test check build up down logs ps clean

install:
	$(UV) sync --all-extras

sync:
	$(UV) sync

dev:
	$(UV) run uvicorn model_engine.main:app --reload --host 0.0.0.0 --port 8000

lint:
	$(UV) run ruff check src tests

fmt:
	$(UV) run ruff format src tests
	$(UV) run ruff check --fix src tests

typecheck:
	$(UV) run mypy src

test:
	$(UV) run pytest

check: lint typecheck test

build:
	docker build -t model_engine:latest .

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	rm -rf dist build .mypy_cache .ruff_cache .pytest_cache
