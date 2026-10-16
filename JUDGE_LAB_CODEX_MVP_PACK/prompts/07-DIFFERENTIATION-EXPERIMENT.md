# Codex prompt 07 — prove incremental value at matched budget

## Read first
`AGENTS.md`, `specs/04-METRICS-AND-STATISTICS.md`, `specs/07-BASELINE-AND-EXPERIMENT.md`, `specs/09-COMPETITOR-AND-REUSE.md`, latest handoff.

## Mission
Evaluate H1/H2 rather than merely producing more charts. A positive result is not guaranteed and negative results must be preserved.

## Tasks
1. Pre-register experiments: case population, family-level split, number of independent cases, severity schema, fixed vs targeted attack types, metrics, statistical analysis and stop rules. Lock plan before opening holdout outcomes.
2. Implement a runner accepting frozen B0 and B1 artifacts; verify same subject judge version and rubric or explicitly label mismatches as comparison invalid.
3. Ensure comparisons are matched on model calls, reviewer minutes and other relevant costs. B0 = 200 labeled cases plus conventional evaluation; B1 = Judge Lab workflow. If B1 requires extra resources, compare against B0 with equal resources, not only the cheaper original baseline.
4. Add random-review/fixed-attack comparator where warranted. Quantify incremental **unique verified** serious false accepts per reviewer hour, total review burden, clean-case coverage, false alarms, cost, and uncertainty.
5. Include a direct-to-primary-source competitor capability matrix from `specs/09`. If network is unavailable, record "unverified" and do not invent vendor feature gaps.
6. Document sample bias, correlated variants and assumptions; avoid statistical significance claims when design does not support them. Include paired/clustered comparisons where applicable.

## Testing and truthful reporting
Can execute code on synthetic data for pipeline tests, but **do not claim empirical superiority** unless actual data, human-adjudicated labels and independent held-out probes exist. Write not-performed template otherwise. Ensure zero positive discovery is a valid output and there's no forced go recommendation.

## Exit gate
Deliver `experiments/DIFFERENTIATION-PROTOCOL.md`, executable comparison script, machine-readable report and honest result/NOT_RUN placeholder, `worklogs/07-experiment.md`. Stop for human review.
