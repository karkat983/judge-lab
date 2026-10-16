# 08 — Deliverables and conservative decision gates

## Report contract
Every report must answer: **What judge and rubric, on which dataset, under which conditions, with how many eligible cases, showed which verified failures? What decision can this evidence justify—and what can it NOT justify?**

Required JSON sections:
1. `claim_scope`: single judge task, intended usage and exclusions.
2. `provenance`: hashes of judge/rubric/dataset/labels/splits, versions, local time (UTC ISO), seed.
3. `population`: total, labeled, excluded, test answered/abstained/errored, class balance.
4. `metrics`: confusion matrix, false accept counts/rates, Wilson 95% bounds, coverage, conditional accuracy, kappa status.
5. `slice_metrics`: defect/severity/family where counts permit; mark too-small slices.
6. `probe_results`: validity, baseline-correct denominator, measured outcomes, attack budget and cost, when present.
7. `critical_findings`: independently verified bad cases, stable case IDs and redacted excerpts.
8. `limitations`: sample bias, model-version uncertainty, possible label disagreement, untested threats, external-vendor handling.
9. `decision`: separate deterministic policy evaluation result, not LLM endorsement.

Report content must be generated from structured numeric data, not free-form LLM speculation. A narrative summary can be generated deterministically with templates; no new "Assurance Composer Agent" needed.

## Gate statuses
- `PASS`: all **policy-defined scoped** preconditions and thresholds pass; does NOT mean universal safety.
- `FAIL`: a required deterministic rule fails or a validated critical failure violates an explicitly specified zero-tolerance rule.
- `REVIEW_REQUIRED`: unresolved high-impact exceptions or human approval needed despite enough data for some checks.
- `INCONCLUSIVE`: missing reference labels, too few cases, undefined core metric, absent holdout, too-wide uncertainty or unperformed required evaluation.
- `ERROR`: invalid report/schema, integrity mismatch, computing failure; not the same as empirical failure.

**Conservative rule:** `ERROR`, `INCONCLUSIVE` and `REVIEW_REQUIRED` must return a CI non-success status unless the caller explicitly provides a manual override (human-logged, policy-bound). Document distinct process exit codes and enforce them with tests.

## Example policy (illustrative only)
```yaml
schema_version: '1.0'
policy_id: incident-judge-pilot
required_dataset_split: heldout_test
minimum_reference_reject_cases: 50
minimum_answer_coverage: 0.95
maximum_false_accept_wilson_upper: 0.08
no_unresolved_critical_case: true
missing_required_probe_behavior: INCONCLUSIVE
human_override_required: true
```
This policy is an **example of syntax**, not a risk tolerance recommendation; with only 50 REJECT cases a Wilson bound as strict as 0.08 may frequently be impossible to pass. Keep the infeasibility visible; never relax controls silently to obtain green.

## Required negative tests
- 100% conditional accuracy with 50% coverage cannot pass high-coverage gate.
- No false accepts among too few cases does not pass strict uncertainty bound.
- Missing held-out data cannot silently pass.
- An injected report saying `"decision":"PASS"` cannot influence policy outcome.
- Invalid artifact digest or missing critical test fails closed.
- HTML escapes report text; no raw secrets; reproducible hashes are recorded.

## Liability and language
Call the output a **reliability evaluation report** or **scoped evidence report**. Do not call it formal certification, compliance approval, indemnification, or a guarantee of production safety. Recommend human deployment authority and explicit incident/postmortem follow-up workflow.
