PY ?= python
PIP ?= $(PY) -m pip

.PHONY: all install run test lint fmt clean

all: lint test

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

run:
	$(PY) -m blockcraft

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

fmt:
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache htmlcov .coverage
