VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
APP ?= dcs_theater_engine.api.app:create_app
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: help venv install test lint check run dev

help:
	@printf "Targets:\n"
	@printf "  make install  Create .venv and install dev dependencies\n"
	@printf "  make test     Run the test suite\n"
	@printf "  make lint     Run Ruff checks\n"
	@printf "  make check    Run lint and tests\n"
	@printf "  make run      Start the API/UI server\n"
	@printf "  make dev      Start the API/UI server with reload\n"

venv:
	python3 -m venv $(VENV)

install: venv
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

check: lint test

run:
	$(PYTHON) -m uvicorn "$(APP)" --factory --host $(HOST) --port $(PORT)

dev:
	$(PYTHON) -m uvicorn "$(APP)" --factory --reload --host $(HOST) --port $(PORT)
