# Roadmap — three evidence-producing stages

## The sequence (implement in this exact order)

| ID | Task / prompt | Evidence and exit gate | Stage |
|---|---|---|---|
| 00 | REPO-AUDIT | repository inventory, no silent overwrite, ADRs | A |
| 01 | BOOTSTRAP-CONTRACTS | validated v1 schemas, positive/negative fixture tests | A |
| 02 | JUDGE-RUNNER | deterministic adapter and imported predictions, bounded I/O | A |
| 03 | CALIBRATION-METRICS | golden numeric tests, undefined-case behavior, 95% intervals | A |
| 04 | REPORT-CLI | single offline command produces truthful JSON + HTML | A |
| 05 | BASELINE-REPLICATION | frozen 200-case selection protocol and reproducible comparison | A |
| 06 | CONTROLLED-PROBES | attacks/perturbations with independently checked validity | B |
| 07 | DIFFERENTIATION-EXPERIMENT | cost-matched baseline, held-out experiment and complete result template | B |
| 08 | RELEASE-GATE | conservative deterministic policy + fail-safe tests | B |
| 09 | PILOT-READY | opt-in intake + study protocol + feedback ledger | C |
| 10 | INDEPENDENT-REVIEW | external-ready security/statistics/report review | C |

### Stage A — Replicate the simple baseline before claiming extra value
- Deliver BYO judge and labels + local CLI.
- Reproduce "customer judge + 200 hand-labeled examples" as reference: use an actually sourced/approved 200-case set when available. An artificial mock fixture can exercise code but cannot count as an empirical baseline.
- Demonstrate correctness with independently calculated goldens; include counts and confidence bounds.
- **Gate A:** no broken tests; all labels and split rules are recorded; a reviewer can reproduce report from fresh clone; missing empirical labels described as a blocker rather than made up.

### Stage B — Prove added value, not extra screens
- Add a small set of controlled transformations and fixed adversarial tests with immutable reference truth and independent oracles.
- Compare extra failure discoveries and review cost against the same judge assessed with conventional baseline evaluation under matched budget; reserve unseen cases.
- **Gate B:** report at least one completed, falsifiable comparison using REAL measured data if available, or explicitly state evaluation is unperformed. A negative result is acceptable; invented wins are not.

### Stage C — Five user pilots, then go/no-go
- Pilot target: **five real humans** fitting the user profile. They may choose not to participate; do not count AI personas or fictional interviews.
- Human runs recruitment and consent. Codex supports local onboarding, feedback capture, import of de-identified results, summary without fake evidence.
- **Gate C:** at least five completed pilots for the intended validation claim; measure real workflow value, annotation and review time, adoption barriers, and repeat usage intent; then decide **ship, reposition, narrow, or stop**.

## Explicit stop / pivot triggers
1. No verified incremental failures or materially lower review cost compared with baseline.
2. Additional findings are invalid, due to corrupted labels, or irreproducible.
3. False-positive/review burden exceeds user value in practical pilot workflows.
4. Prospective users will not provide labels or cannot legally use the tool on their data.
5. Competitor/standard tool already achieves the tested benefit without meaningful cost or workflow advantage.

## Never infer
Five pilots are not scientifically conclusive evidence of broad market demand. A PASS gate never predicts zero production incidents; it means only that the stated policy and scoped tests passed.
