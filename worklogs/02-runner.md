# Phase 02 — offline runner and prediction import

User authorized phases 02–10, commits and pushes; this supersedes the previous
per-phase pause. Existing scientific/human-evidence requirements remain intact.

Implemented `runner.py`: typed blind-input adapter protocol, deterministic narrow
mock, exact label parser, normalized result binding, exact case-ID imports,
call-budget/cancellation checks and terminated-process timeouts for trusted custom
test adapters. No model API or paid adapter is executable from the CLI. Adapters
return private replies; only the runner can bind case/reference provenance to a
JudgeResult. This completes the proposed interface without sending references to
the judge. Positive or unknown reported spend stops further calls and yields ERROR;
future paid providers require reservation accounting before dispatch.

`artifacts.py` writes owned bundles through sibling staging directories and atomic
rename; existing directories require explicit overwrite and the ownership marker.
Traversal, symlinks, unowned output and collisions reject. Interrupted replacement
rolls back. No arbitrary generated shell or downloaded source executes.

Validation (actual exits):

- `pytest -q tests/contracts`: 128 passed, exit 0 (1.40s).
- `make typecheck`: exit 0, seven source files.
- Initial Ruff: two import-order findings, fixed; `make lint`: exit 0.
- API smoke imported 10 constructed predictions into `runs/phase02-import/`:
  normalized JSONL plus manifest, preserving ABSTAIN/PARSE_ERROR, exit 0.

Tests cover parser contamination, invalid/missing/duplicate/mixed provenance,
determinism, exhausted budgets, cancellation, process timeout, path/symlink and
atomic overwrite boundaries. Generated outputs remain ignored. Existing code was
preserved. Engineering gate complete; no empirical performance claim. Next: 03.
