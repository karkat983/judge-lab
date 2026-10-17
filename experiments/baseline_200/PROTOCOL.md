# Baseline 200 protocol v1 — freeze before viewing predictions

Status: tooling available; empirical execution NOT PERFORMED. Target: authorized
security-investigation reports judged under one frozen evidence/allowed-action rubric.
Unit: independent source incident family, not a report variant. Human owner must
confirm provenance, rights and intended population; code cannot authenticate these claims.

1. Define population, severity/error taxonomy and source permissions before import.
   Group all variants of an incident into one family and one split. Development,
   calibration_200 and heldout_test must be disjoint. Reserve sealed holdout before tuning.
2. Two human reviewers independently annotate each candidate blind to judge outputs.
   Record reviewer IDs/labels and disagreement. An identified adjudicator resolves
   conflicts; disputed records block baseline input. Frozen records bind case digests.
   No model-generated labels or synthetic fixtures count as human annotations.
3. Predeclare seed 44 and protocol revision baseline-v1. Sort family IDs; sample 200
   calibration families without replacement; choose lowest stable case ID per family.
   This is an unweighted family sample, not a prevalence-corrected stratified estimate.
   Too few families is an explicit failure; do not duplicate cases to reach 200.
4. `python -m judge_lab.baseline select --data POOL.jsonl --manifest POOL.json
   --labels HUMAN_LABELS.jsonl --out runs/selection` writes a frozen selection,
   selected dataset/manifest and matching annotations. Archive the selection digest
   before generating any judge predictions; use read-only permissions in the workflow.
5. Use the normal calibration runner with the selected dataset. Freeze judge/spec/
   model/parser/adapter/run metadata and retain normalized imported predictions.
   `python -m judge_lab.baseline evaluate --data SELECTED.jsonl --manifest SELECTED.json
   --labels SELECTED_LABELS.jsonl --selection SELECTION.json --run-manifest RUN.json
   --predictions PREDICTIONS.jsonl --reviewer-minutes ACTUAL_MINUTES --out runs/b0`
   validates exactly 200 families and records the human-supplied review-cost ledger.
6. Compare counts with an ordinary Python loop independent of Judge Lab. Report
   false accepts, coverage, undefined metrics and uncertainty; zero failures does
   not prove safety. Family grouping and annotation truth require human review.

The selection digest binds source pool, annotation records, seed and protocol.
It is not a trusted timestamp or signature: it cannot stop an authorized operator
from rerunning selection after viewing predictions. Record the preregistration in
version control before prediction collection and disclose protocol deviations.
