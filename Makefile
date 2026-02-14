.PHONY: lint format md-lint test coverage

PACKAGE = scrapyduler
PYTHON = python3

lint:
	$(PYTHON) -m ruff check $(PACKAGE) tests
	$(PYTHON) -m ruff format --check --diff $(PACKAGE) tests

format:
	$(PYTHON) -m ruff check --fix $(PACKAGE) tests
	$(PYTHON) -m ruff format $(PACKAGE) tests

md-lint:
	$(PYTHON) -m mdformat --check README.md

test: lint
	$(PYTHON) -m pytest tests $(ARGS)

coverage: lint md-lint
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=xml --cov-report=term-missing --cov-fail-under=100 tests $(ARGS)
