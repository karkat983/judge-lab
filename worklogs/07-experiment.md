# Phase 07 — matched-budget evidence comparison

Implemented `judge_lab.experiments` with frozen plan/ledger/finding contracts and
same-subject, rubric, dataset, label/split and observation checks. Requires a
200-family calibration artifact, disjoint holdout, equal calls/tokens/cost/reviewer
minutes, independently attested false accepts, and deduplication by family/type.
Exports paired family discoveries, rates, review burden, coverage and fixed
limitations. Zero and negative increments remain valid; no superiority inference.

Added preregistration/stop/severity protocol, machine-readable NOT_RUN record and
six-product official-source capability matrix checked 2026-10-17. No vendor API or
account access. The matrix makes no claims of missing incumbent functionality.

Executed 7 comparison tests: all passed, exit 0. Tests cover zero discovery,
negative results, duplicate discoveries, version/rubric/data mismatch, unequal
budget, family leakage and no-data status. `make lint` pass; `make typecheck` pass
(15 modules). CLI `python -m judge_lab.experiments --out runs/phase07-not-performed`
printed NOT_PERFORMED, exit 4, wrote comparison.json.

Scope decision: compare review workflows on identical frozen subject observations
in v1. Novel transformed probe datasets require a reviewed paired-mapping contract
and independent labels; H2 empirical analysis remains NOT PERFORMED. No false
claim that same-case comparison measures novel probe effectiveness. Supplied
reviewer/budget attestations need independent authentication; no trusted timestamp
service is introduced. Primary discovery intervals are omitted because targeted
review is not an independent random sample. External B0/H1/H2 evidence unavailable.
Next authorized phase: 08 deterministic conservative gate.
