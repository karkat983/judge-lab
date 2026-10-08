# Common tasks. Run `make help` for a list.
PYTHON ?= .venv/bin/python

.PHONY: help setup data test clean

help:      ## list targets
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

setup:     ## create .venv and install dependencies
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

data:      ## download XSTest and rebuild the 200-prompt sample
	$(PYTHON) scripts/fetch_data.py

test:      ## offline unit tests (no LLM calls)
	$(PYTHON) -m pytest -q -m "not live"

clean:     ## delete raw downloads and cached judgments
	rm -rf data/raw data/cache
