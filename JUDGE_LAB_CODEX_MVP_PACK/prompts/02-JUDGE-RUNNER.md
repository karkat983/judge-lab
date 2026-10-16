# Codex prompt 02 — deterministic judge runner and prediction import

## Read first
`AGENTS.md`, latest worklog, `specs/02-ARCHITECTURE.md`, `specs/03-DATA-CONTRACTS.md`, `specs/06-SECURITY-BOUNDARIES.md`.

## Goal
Build provider-independent, reproducible plumbing before depending on real LLM performance.

## Tasks
1. Define `JudgeAdapter` protocol and `evaluate(case_view, judge_spec) -> JudgeResult` without exposing reference labels; enforce per-case ID consistency.
2. Implement `DeterministicMockAdapter` for synthetic fixtures with a documented rule or fixture lookup. This is a **test double**, not scientific evidence of evaluator capability.
3. Support importing prediction JSONL with exact `case_id` joins; reject unexpected, missing, duplicate, mixed-run or mismatched-case predictions. Preserve case ordering by stable IDs.
4. Implement strict label-only parser for `ACCEPT/REJECT/ABSTAIN`; malformed model output -> typed parse ERROR. Ensure no hidden fallback converts failures to REJECT.
5. Implement bounded calls, cancellation/timeout interface, and accounting counters; mock is network-free. **Live provider adapter optional future opt-in** and must not be added merely to claim coverage.
6. Store separate run metadata and normalized JudgeResult objects with digest/source provenance; use atomic writes for artifacts.

## Negative cases
Unknown case ID; duplicate prediction; parser contamination (`ACCEPT because...`, JSON with suspicious extras where strict mode forbids it); nonsensical Unicode; empty response; timeout; budget exhaustion; mock revealing label leak; malicious instructions preserved as inert content.

## Exit gate
Use imported predictions to produce a case-by-case normalized result file, test deterministic repeatability, record actual successful and failed test commands in `worklogs/02-runner.md`. Do not yet compute assurance scores or implement gate decisions.
