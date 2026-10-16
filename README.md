# judge-lab

> Status: **Phase 01 contracts implemented.** Offline security-investigation schemas,
> JSONL validation and provenance are available as `judge_lab`. The judge runner,
> calibration reports and release gates are later phases.

The current MVP evaluates judges of **security-investigation reports** using separate
`ACCEPT` / `REJECT` references and `ACCEPT` / `REJECT` / `ABSTAIN` predictions.
Execution failures are typed `ERROR` outcomes. The existing XSTest safe/unsafe
experiment remains under `src.*` and is described below as legacy functionality.
See the [roadmap](ROADMAP.md), [contract guide](docs/contracts-v1.md), and
[Phase 01 handoff](worklogs/01-bootstrap-contracts.md).

## Phase 01: install and validate offline

Use Python 3.12 or newer. Dependency installation needs package-index access;
the smoke check and tests make no model calls.

```bash
make setup
make test
make lint
make typecheck
.venv/bin/python - <<'PY'
from pathlib import Path
from judge_lab.load import load_dataset
dataset = load_dataset(Path("examples/security_fixture.jsonl"),
                       Path("examples/security_manifest.json"))
print(dataset.summary())
PY
```

The ten bundled cases and example outcomes are **synthetic code fixtures, not
empirical judge results or human-adjudicated benchmark evidence**. Nothing in
Phase 01 makes a release decision. No `judge-lab` CLI is implemented yet.
The public input format in this phase is JSON/JSONL; legacy CSV is not silently converted.

`requirements-dev.lock` pins the tested development environment. `pyproject.toml`
declares the minimal runtime dependency and separate dev/legacy extras. The old
`requirements.txt` remains available for the legacy provider workflow.

## Legacy XSTest experiment

## Problem
LLMs are increasingly used to grade other models' outputs, but a grader is only useful if its verdicts track human judgement and cannot be steered by the text it is grading. This matters because safety evaluations, leaderboards and guardrails all inherit whatever bias or weakness the judge has. See Zheng et al. 2023, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena".

## Approach
*Planned.* Run an LLM judge over a labelled public set of safe and unsafe prompts (XSTest), measure agreement with the human labels (accuracy, Cohen's kappa), test position and verbosity bias, and test whether an instruction hidden in the graded text flips the verdict.

## Results
*Planned.* No numbers yet.

| Metric | Value |
|--------|-------|
| Judge vs human accuracy | — |
| Cohen's kappa | — |
| Verdict flip rate under swap | — |
| Judge-injection success rate | — |

## Legacy setup (optional)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_data.py     # XSTest -> stratified 200-prompt sample in data/prompts.csv
pytest -m "not live"
```
The legacy judge plumbing exists; empirical judge runs, bias and injection results
remain unreported. The data download is unnecessary for Phase 01.

## What I learned
*Planned.*

## Notes
Public data only (XSTest, Röttger et al. 2024, CC BY 4.0). Not affiliated with any employer. Built October 2026.

## Changelog
- Day 1: project scaffold and changelog; XSTest sampler, loader, agreement stats.
- Committed the 200-prompt sample with source, licence and data card; label review of 30 items
  (28 agree, 2 ambiguous, 0 clear disagreements; docs/label_review.md).
- LLM layer: local Ollama judge by default (qwen2.5:3b-instruct), Claude optional; cache, cost
  meter, retry with backoff, rate limiting, scripted fake LLM for tests.
- Statistics: Cohen's kappa checked against its definition, bootstrap CI (coverage-tested),
  balanced accuracy and precision/recall for the unsafe class.
