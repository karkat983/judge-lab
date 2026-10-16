# 10 — Five real-user pilot protocol (no invented adoption)

## Recruitment hypothesis
Aim for five practitioners who own LLM-judge evaluations of security or incident analysis: AI eval engineer, security tooling engineer, SOC automation lead, or responsible researcher. Recruit humans through user-managed networks; Codex creates scripts/templates but cannot contact anyone without authorized app access or human execution.

## Screening and permission
Ask if they (a) own a real judge and labeled examples; (b) can use synthetic/deidentified cases in local tool; (c) have budget/time to compare methods; (d) consent to anonymized feedback capture; (e) can approve data-handling. Do not require them to expose employer secrets.

## Pilot structure
1. Brief product capability and limits; identify their existing evaluation workflow and *what they paid/used* previously, without inventing procurement evidence.
2. Run conventional baseline with their judge/labels or agreed synthetic evaluation, recording setup time.
3. Run Judge Lab under comparable conditions, recording setup, reviewer time, real failure discoveries, invalid findings and blockers.
4. Conduct structured debrief: decision changed? which failure new? would they use again? what was confusing? data constraints? willing to pay for which outcome?
5. Record observed data distinct from opinions/estimates. No fictitious testimonials.

## Pilot record schema
`pilot_id` (pseudonym), `role`, `industry` (optional coarse), `consent_record`, `dataset_permissions`, `workflow_before`, `task_minutes`, `setup_minutes`, `labels_used`, `baseline_findings_confirmed`, `judge_lab_findings_confirmed`, `invalid_findings`, `rejected_findings`, `incremental_reviewer_minutes`, `pricing_signal`, `qualitative_feedback`, `observed_decision_change`, `date`, `source_of_claim`.

## Data practice
Local-only by default. No upload of raw company data. Any survey responses include permission to quote and de-identification; permit withdrawal according to agreed protocol. Reports must clearly label `NO REAL PILOT DATA` until observed.

## Pilot success/failure interpretation
Five pilots provide early usability and value evidence, **not** definitive statistical validation. Signals: users independently reproduce output, verified extra findings, less total review burden, workflow integration, repeat usage. Negative signal: no labels, no need beyond existing tools, no incrementally verified errors, privacy blockers.

## Decision memo
After pilot #5, recommend one of: (a) narrow and ship local tool; (b) integrate with incumbent platform; (c) pivot use case; (d) stop. Provide evidence table, caveats, and disconfirming signals. No default 'proceed' recommendation.
