# Codex prompt 03 — mathematically correct calibration engine

## Read first
`AGENTS.md`, `specs/03-DATA-CONTRACTS.md`, `specs/04-METRICS-AND-STATISTICS.md`, latest run handoff.

## Goal
Build pure functions and independently verified metrics that can be trusted more than any generated narrative.

## Tasks
- Compute four 2x2 answered confusion counts AA, AR, RA, RR, plus ABSTAIN/ERROR by reference class, from frozen reference and normalized predictions.
- Define unconditional/conditional denominators exactly as `specs/04` states; include conditional accuracy, overall-case correctness, coverage, false accept rate on answered reference REJECT cases, false reject rate, precision of accepted judgments, and Cohen's kappa. Mark undefined metrics with reason; no NaN leaked to JSON.
- Implement Wilson 95% intervals for binomial proportions with independently calculated tests. Do not overpromise interval validity for correlated probe variants.
- Allow slicing by authoritative metadata (case severity, error type, incident family) without averaging differently sized slices into misleading global claims; mark small sample explicitly.
- Emit machine-readable counts and calculated metrics with documentation of formula and denominator.

## Tests required
The four golden fixtures in `specs/04`; all ACCEPT (kappa undefined); empty sample; no REJECT reference class; all ABSTAIN; all ERROR; zero false accepts among 20 (upper interval >0); class imbalance; mismatched IDs; repeated incident variants; integer precision and deterministic sort.

## Independence check
If using a library for metrics, independently implement a small test reference in tests or manual golden examples; do not copy the production function into its test. Ensure results do not depend on generated judge explanation.

## Output and gate
Run unit + property-based tests if available, type/lint checks. Produce a tiny **synthetic-only** example report from known fixtures. Log tests and interpretations in `worklogs/03-metrics.md`; STOP after math correctness gate.
