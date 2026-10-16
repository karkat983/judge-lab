# Codex prompt 08 — deterministic CI gate with conservative abstention

## Read first
`AGENTS.md`, `specs/08-REPORTS-AND-DECISION-GATES.md`, `specs/04-METRICS-AND-STATISTICS.md`, latest handoff.

## Mission
Translate scoped measured evidence into a **policy-specific** CI decision. A green gate does not certify system safety.

## Implement
- YAML policy validation; immutable thresholds and minimum class counts; reference/data/split requirements.
- Pure `evaluate_gate(report, policy)` without LLM calls. `PASS/FAIL/REVIEW_REQUIRED/INCONCLUSIVE/ERROR` with machine-readable reasons, policy version and report digest.
- CLI `judge-lab gate --report <json> --policy <yaml>`, distinct exit statuses; non-PASS default exit nonzero for automated CI. Document policy override authorization and audit record, but do not implement an untracked bypass.
- Support predeclared critical defect rule and uncertainty bound threshold. A small sample with observed zero failures **must not** imply safety.
- Compare baseline/candidate only if judge, rubrics and dataset comparability requirements are satisfied; otherwise INCONCLUSIVE.

## Required acceptance tests
No holdout -> INCONCLUSIVE; class n under threshold -> INCONCLUSIVE; Wilson bound exceeds limit -> FAIL; known critical finding => FAIL or REVIEW_REQUIRED as policy specifies; tampered report => ERROR; attempted text in report setting `PASS` => ignored; human override without record => denied; policy change invalidates previous decision.

## Gate
Build tests + example CI workflow using offline fixture, do not include live deploy actions. Document actual results in `worklogs/08-gate.md`; stop before any production integration.
