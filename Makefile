.PHONY: install run test test-api test-e2e test-smoke clean help

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies and Playwright browser binaries"
	@echo "  make run         - Run the PulseOps Hub service locally on http://127.0.0.1:8000"
	@echo "  make test        - Run all automated tests (API + E2E)"
	@echo "  make test-api    - Run API test suite"
	@echo "  make test-e2e    - Run Playwright E2E test suite"
	@echo "  make test-smoke  - Run quick smoke tests"
	@echo "  make clean       - Remove cache and SQLite database artifacts"

install:
	uv sync
	uv run playwright install chromium

run:
	uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	uv run pytest

test-api:
	uv run pytest tests/api -m api

test-e2e:
	uv run pytest tests/e2e -m e2e

test-smoke:
	uv run pytest -m smoke

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ pulseops.db
	find . -type d -name "__pycache__" -exec rm -rf {} +
