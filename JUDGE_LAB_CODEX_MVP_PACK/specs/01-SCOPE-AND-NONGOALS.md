# 01 — Scope, customer workflow, hypotheses, non-goals

## Product contract
Input: (a) user's judge specification OR imported predictions, (b) a versioned dataset of security-investigation reports with independently adjudicated `ACCEPT` / `REJECT` references, (c) a rubric, (d) optional controlled probe cases and policy.

Output: a portable evidence bundle with per-case predictions, parser/error outcomes, scoped reliability metrics, uncertainty intervals, adversarial probe validity and results (when tested), a human-readable audit report, and an optional deterministic CI gate.

The product **tests the reliability of a customer's evaluator for a particular task and dataset**. It does not decide if arbitrary AI systems are safe. The evaluation target is a judge model+prompt+parser+rubric+version, not just a model brand.

## Initial controlled domain: security-investigation report evaluator
Given a report and trusted case metadata, judges must decide whether it meets a fixed rubric. Examples of unacceptable reports:
- Cites an alert or log that the provided authoritative evidence does not contain.
- Declares an unsupported root cause with unjustified certainty.
- Recommends an explicitly unauthorized production action despite allowed-action constraints.
- Omits evidence specifically required by the rubric for the case.

A report's `reference_label` comes from independent human adjudication and/or mechanically verifiable, scoped case rules, NOT the judge under evaluation. Human reviewers resolve complex factual ambiguity. Record disagreement and adjudication status; exclude or mark disputed cases per protocol, not after seeing model results.

## Two research hypotheses only
- H1: error characterization/targeted review improves decision-relevant failure discovery or expert reviewing effort relative to 200-labeled-example baseline.
- H2: validated adversarial probes uncover held-out, independently proven failures beyond fixed-attack baseline at comparable execution/review cost.

## v0.x in-scope
- Local CSV/JSONL import and manifest validation; reference label provenance; frozen split identifiers.
- Mock judge, imported predictions; one provider adapter later behind explicit permission.
- Strict verdict parsing `ACCEPT`, `REJECT`, `ABSTAIN`, `ERROR` (ERROR from system, not an output label).
- Binary confusion, coverage, conditional metrics, uncertainty, kappa, structured errors.
- Reproducible JSON and self-contained HTML report; CLI and Python API.
- Deterministic controlled probes with fixed tests, independent validity oracle.
- Policy-based gate where missing evidence → INCONCLUSIVE or REVIEW_REQUIRED.
- Anonymized pilot data import and export.

## Out of scope until empirical gate approval
- Universal "AI assurance" or certification; insurance, legal, medical, robotics, aerospace, finance domain-specific certifications.
- Multi-agent workflow engine, causal investigator agent, autonomous adversarial-agent generator, autonomous fix agent.
- Production incident actions, access to private cloud/SOC tools, high-impact autonomous execution.
- Broad general-agent trace analysis; production streaming platform; enterprise dashboard, SSO, tenancy.
- Model fine-tuning, judge weighted voting, "reliability score" used as universal probability of safety.

## Deliverable / accountability semantics
Artifact claims must bind to dataset/label source and version, rubric version, judge model+settings, run environment, date, metrics and known exclusions. Use `"eligible_for_release": false` when policy cannot confidently pass; no claims of liability guarantee. Caller makes final deployment decision. Maintain a documented incident-reporting and correction process, without implying insurance.

## Non-goal decision test
Before adding a feature: *Which named pilot user requested it? Which falsifiable claim requires it? What baseline will demonstrate value? Can a smaller deterministic check accomplish the same?* A feature without a defensible answer belongs in `reference/`, not implementation.
