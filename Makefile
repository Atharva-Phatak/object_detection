.PHONY: setup download-model run-dev run-prod run-sql stop test lint

setup:
	uv sync

download-model:
	bash scripts/download_models.sh

run-dev:
	PYTHONPATH=. ENV=dev uv run python -m counter.entrypoints.webapp

run-sql:
	docker compose --profile sql pull && docker compose --profile sql up

run-prod:
	docker compose --profile prod pull && docker compose --profile prod up

stop:
	docker compose down

clean:
	docker compose down -v  # removes volumes too

test:
	uv run pytest

lint:
	uv run ruff check .
