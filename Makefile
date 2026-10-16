# Common tasks. Run `make help` for a list.
PYTHON ?= .venv/bin/python

.PHONY: help setup data lint test typecheck clean

help:      ## list targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

setup:     ## create .venv and install the package and offline development dependencies
	python3 -m venv .venv
	$(PYTHON) -m pip install -r requirements-dev.lock
	$(PYTHON) -m pip install --no-build-isolation -e ".[dev,legacy]"

data:      ## download XSTest and rebuild the 200-prompt sample
	$(PYTHON) scripts/fetch_data.py

lint:      ## ruff lint
	$(PYTHON) -m ruff check .

test:      ## offline unit tests (no LLM calls)
	$(PYTHON) -m pytest -q -m "not live"

typecheck: ## strict typing for the new package (legacy src.* remains separate)
	$(PYTHON) -m mypy src/judge_lab

clean:     ## delete raw downloads and cached judgments
	rm -rf data/raw data/cache
