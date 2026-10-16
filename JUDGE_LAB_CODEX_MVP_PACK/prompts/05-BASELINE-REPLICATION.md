# Codex prompt 05 — baseline 200 labels, no imaginary ground truth

## Read first
`AGENTS.md`, `specs/07-BASELINE-AND-EXPERIMENT.md`, `specs/09-COMPETITOR-AND-REUSE.md`, and latest handoff.

## Goal
Replicate the ordinary solution Judge Lab must beat: a customer's frozen judge evaluated on 200 independently labeled examples.

## Implement
1. `experiments/baseline_200/PROTOCOL.md` defining target population, scenario family grouping, label instructions, exclusion rules, adjudication plan, sample allocation, random seed and pre-registration.
2. Script to sample at most 200 **independent case families** from an **authorized** labeled pool using a recorded seed; require source provenance. Refuse to silently fabricate or relabel duplicates to reach 200.
3. Script to import human adjudication records, record disagreement, adjudication status and label freeze. Do NOT use target judge to produce "human" labels.
4. Script using the existing calibration kernel to evaluate a frozen judge + exactly those 200 when available; produce B0 counts, metrics and reviewer-cost ledger.
5. `NOT_RUN.md` clearly stating external data unavailable if we have no truly human-labeled 200-case pool; still demo workflow on synthetic fixture for code correctness.
6. Compare implementation with a simple baseline Python evaluation function to ensure Judge Lab is not just rebranding ordinary metrics.

## Guardrail
Do not assume that 200 independent labels give precise estimates of rare failure rates. Show uncertainty and label consistency, or keep the evidence inconclusive.

## Tests
Sample reproducibility; family split disjointness; no leaked held-out cases; can't choose selected dataset after seeing predictions; duplicate/insufficient labels -> explicit status; prevented automated conversion of synthetic labels into claimed human annotations.

## Exit gate
Baseline reproducible from available source (or clearly NOT RUN); research/evidence gap and human data needs in `worklogs/05-baseline.md`. Stop; do not start advanced probes before baseline and protocol are reviewed.
