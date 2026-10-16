# Stage A — Baseline replication, not novelty theater

**Execute prompts 00–05 sequentially.** Goal: testably correct, usable calibration runner, where the ordinary competitor is 200 human-labelled cases and a confusion matrix. Nothing "agentic" is needed.

## Inputs
Old repo (may be empty), project plan, synthetic fixtures, user-provided approved label sources if they exist, rubric and exact judge spec.

## Expected artifact tree
```
pyproject.toml
src/judge_lab/...
examples/security_fixture.jsonl
examples/mock_judge.yaml
tests/unit/... tests/integration/... tests/security/...
experiments/baseline_200/PROTOCOL.md
runs/demo/report.json         # generated, gitignored
runs/demo/report.html         # generated, gitignored
worklogs/00...05...
```

## Measurement standards
- Golden hand-checked metric fixtures pass.
- Confusion cells and reasons match contract; no path hides false ACCEPT outcomes.
- Wrong/absent labels must not become reference truth; dataset partitioning and provenance explicit.
- Baseline performance is not "proven" by synthetic fixture.
- A README newcomer can run an offline demo with no provider credentials.

## Stage A acceptance decision
`READY`: stable validated contracts, CLI, metrics, report and truthful baseline artifacts. `BLOCKED`: fundamental code/test failures. `INCONCLUSIVE`: functioning demo but empirical 200 human labels unavailable. The latter can be a legitimate engineering completion, NOT empirical validation.

**Human gate:** approve moving to probes only after reviewing metrics and limitations.
