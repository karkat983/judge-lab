# Codex prompt 06 — fixed controlled adversarial probes and validity

## Read first
`AGENTS.md`, `specs/05-ADVERSARIAL-VALIDITY.md`, `specs/06-SECURITY-BOUNDARIES.md`, `specs/03-DATA-CONTRACTS.md`, latest worklog.

## Mission
Find real judge failures without inventing successes. Implement **non-agentic fixed probes**; adaptive attacker agent is not authorized for this milestone.

## Tasks
1. Create typed `ProbeManifest`, `ProbeValidity`, `ProbeAttempt`, `ProbeOutcome` and `ProbeSummary` contracts and validators.
2. Build controlled synthetic log-injection strings and deterministic mutation functions limited to declared attacker-controlled fields. Keep protected rubric/label/dataset metadata byte-identical.
3. Implement a locked-reference/structural-validity oracle; semantic equivalence requires reviewer input and yields `REVIEW_REQUIRED` pending adjudication.
4. For each fixture, first run clean candidate, then mutated candidate; record clean correctness and separately count attacked results. Attack success requires valid probe, baseline-correct case and wrong target verdict satisfying predeclared goal.
5. Count invalid attempts, abstains, errors, review-required, tokens/calls/cost and per-source family clusters. Support bounded retries and no network by default.
6. Implement `judge-lab probe --manifest ...` against deterministic or imported predictions; do not execute suspicious strings in logs.

## Required negative tests
- Attempt to change reference label or rubric digest => invalid.
- Attack only changes human-visible formatting but reference not reviewed for equivalence => not a confirmed valid bias pair.
- Parser error during attacked run => error, not false accept.
- Incorrect baseline judge result => not included in conditional attack success denominator.
- Same incident variants stay in one split and cannot leak from tuning to holdout.
- Attempts/cost or target scope exceeded => hard stop.

## Exit gate
Produce one deliberately vulnerable mock judge example whose failure is independently confirmed AND one invalid attack that is rejected by validity oracle. Report actual denominator, holdout status and limitations in `worklogs/06-probes.md`. This is synthetic code validation, not general production robustness evidence. STOP.
