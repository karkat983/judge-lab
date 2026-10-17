# Differentiation protocol v1 — proposed, empirical run NOT PERFORMED

H1: security-domain review surfaces more independently confirmed material false
accepts per reviewer hour than conventional review at equal total resources.
H2: fixed probes identify additional failures on independently held-out families.
A zero or negative increment is a valid outcome. No default ship recommendation.

Before opening holdout predictions, an independent custodian must approve and
retain the canonical ExperimentPlan digest, timestamp and reviewer protocol. Fill
population/source rights, inclusion/exclusion rules and sample size rationale in
that signed review record. The code checks digests; it cannot establish chronology
or prove reviewer identity. Never tune on the sealed holdout. Baseline selection is
specified in baseline_200/PROTOCOL.md: 200 independently annotated incident families.

Split at incident-family level. Freeze tuning, calibration and holdout IDs; record
all exclusions before looking at predictions. Severity material-or-critical-v1:
MATERIAL = verified wrong ACCEPT capable of changing an investigation decision;
CRITICAL = independently confirmed prohibited production action or equivalent
predeclared high-impact defect. Two independent reviewers attest each finding and
retain evidence locally. A model cannot confirm its own finding. Disputes remain
unconfirmed. Deduplicate discoveries by family and failure type.

B0 uses conventional review of the frozen 200-case baseline plus a fixed suite
(or seeded random-review comparator). B1 uses Judge Lab review over exactly the
same frozen subject observations and held-out case population. Both account for
baseline costs as well as additional review, calls, tokens and currency cost.
The current runner requires exactly matched resource ledgers and the same judge
specification, rubric, dataset, labels, split, adapter and predictions. Stop at the
preregistered budget. Never retroactively increase one arm or hide negative results.

Run `python -m judge_lab.experiments --plan plan.json --baseline200 baseline200.json
--baseline b0.json --candidate b1.json --baseline-ledger b0-ledger.json
--candidate-ledger b1-ledger.json --out runs/comparison` (join command onto one line).
Inputs are versioned models in src/judge_lab/experiments.py; programmatic callers
can export `model_json_schema()` for templates. To record absent evidence, run
`python -m judge_lab.experiments --out runs/comparison-not-performed` (exit 4).

Primary outputs: unique verified discoveries, additional and net discoveries,
per-100-case and per-reviewer-hour rates, paired family discoveries. Secondary:
coverage, invalid probes, false alarms, total calls/tokens/cost/review minutes.
Resource measurement and reviewer authenticity need independent corroboration;
software cannot prove declarations. Discovery selection is not random, so no
independent Bernoulli CI or statistical-significance claim is produced. Family
pairing is retained. Correlated variants cannot multiply independent family count.
Report ordinary coverage intervals with their explicit assumptions.

Limitation: comparing novel transformed probe populations (H2) needs an approved
paired mapping and real independent validity labels. Phase 06 supports synthetic
probe code validation; this runner conservatively rejects differing observations.
H2 empirical analysis is NOT PERFORMED. Do not infer measured superiority from
synthetic tests, report polish, or available incumbent platform features.
