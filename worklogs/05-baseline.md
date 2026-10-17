# Phase 05 — frozen 200-case baseline

Implemented `judge_lab.baseline` select/evaluate commands, strict independent
adjudication records, family-disjoint seeded selection, label and manifest digest
bindings, exact 200-family enforcement, private selected-data bundles, imported
prediction evaluation and measured reviewer-time ledger. Protocol and NOT_RUN
placeholder are in `experiments/baseline_200/`. No real annotations were invented.

Tests initially found that a 200-case report exceeded the 256 KiB record limit.
Fixed report documents with a separate bounded 16 MiB JSON reader; individual
case/config limits remain 256 KiB. Result validation now checks the dataset once
instead of once per row. README sentence corrected.

Executed: `pytest -q tests/contracts/test_baseline.py tests/contracts/test_runner.py`:
17 passed, exit 0; `make lint`: pass, exit 0; `make typecheck`: 13 files, exit 0.
The baseline select command with absent labels printed NOT_PERFORMED and exited 2.
The 200-row integration test uses explicitly manufactured test-only declarations;
it checks bindings, NOT a scientific baseline. A changed reviewer invalidates reuse.

Limitations: hashes need externally trusted expected values; they cannot prove that
reviewers exist or that preregistration preceded predictions. Human data, rights,
independent review and observed reviewer effort remain unavailable. Empirical B0:
NOT PERFORMED. Next authorized phase: 06 fixed controlled probes.
