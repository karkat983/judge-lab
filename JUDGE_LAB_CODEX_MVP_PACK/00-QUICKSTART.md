# How to execute this pack using Codex inside Cursor

## Prepare
1. Create or open your existing `judge-lab` repository in Cursor (root folder open).
2. Copy the **contents** of this pack into the repository root so `AGENTS.md` is at root. Back up or reconcile any existing `AGENTS.md`—do not overwrite useful existing instructions without review.
3. Commit the copied documents separately, e.g. `docs: adopt evidence-first Judge Lab MVP plan`. Keep the original master blueprint under `reference/` as historical reference.
4. Open Codex at repo root. Attach/mention `AGENTS.md` and `prompts/00-REPO-AUDIT.md`.
5. Run the audit prompt **first**. Review its proposed changes and actual diagnostics. Then continue stepwise.

## First message to Codex (copy exactly)
> You are the Judge Lab Implementation Lead. Read `AGENTS.md`, `README.md`, `ROADMAP.md`, `specs/01-SCOPE-AND-NONGOALS.md`, `specs/02-ARCHITECTURE.md`, `specs/03-DATA-CONTRACTS.md`, and `prompts/00-REPO-AUDIT.md`. Inspect the existing repo; do not assume files or tests exist. Execute **only** the repo audit; write the specified worklog and ADRs. Do not start the next implementation phase without a human review of the audit. Show actual command outputs and report blockers truthfully.

## Phase prompts / suggested order
- `prompts/00-REPO-AUDIT.md` — inventory, constraints, conflict resolution.
- `prompts/01-BOOTSTRAP-CONTRACTS.md` — fixture contracts, packaging, tests.
- `prompts/02-JUDGE-RUNNER.md` — mock judge and imported predictions.
- `prompts/03-CALIBRATION-METRICS.md` — exact, independently tested metrics.
- `prompts/04-REPORT-CLI.md` — repeatable report and sample command.
- `prompts/05-BASELINE-REPLICATION.md` — 200-case benchmark protocol, no manufactured measurements.
- `prompts/06-CONTROLLED-PROBES.md` — validity-first injection and perturbations.
- `prompts/07-DIFFERENTIATION-EXPERIMENT.md` — compare with baseline fairly.
- `prompts/08-RELEASE-GATE.md` — conservative deterministic policy.
- `prompts/09-PILOT-READY.md` — human-run five-user pilot tooling.
- `prompts/10-INDEPENDENT-REVIEW.md` — adversarial audit and release decision.

**Each prompt is one bounded task. Stop on completion of its gate.** Codex must not decide that tests passed from intended code; it must run the tests and record actual output.

## Example *target* CLI (not a claim of implemented behavior)
```bash
judge-lab validate --judge examples/mock_judge.yaml --data examples/security_fixture.jsonl
judge-lab calibrate --judge examples/mock_judge.yaml --data examples/security_fixture.jsonl --out runs/demo
judge-lab probe --manifest examples/controlled_probe.yaml --out runs/probe-demo
judge-lab compare --baseline runs/baseline --candidate runs/candidate --out runs/compare
judge-lab gate --report runs/compare/report.json --policy examples/gate_policy.yaml
```
Codex should implement commands incrementally and use `judge_lab` module invocation as a fallback until packaging is complete. Avoid using real provider APIs during early phases.

## Required handoff after each task
`worklogs/NN-title.md` using `templates/HANDOFF.md`, including exact files, commands, pass/fail counts, observed results, limitations, next gate. Commit only after review. If external credentials or human labels are required, create **explicit TODOs** and stop there.
