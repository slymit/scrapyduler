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
	$(PYTHON) -m coverage run --source $(PACKAGE) -m pytest tests $(ARGS)
	$(PYTHON) -m coverage report --show-missing --fail-under 100
