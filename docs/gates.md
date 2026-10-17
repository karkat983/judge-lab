# Scoped policy gates

`judge-lab gate --report runs/demo/report.json --policy examples/gate_policy.yaml`
returns a structured decision. `--evidence` supplies a separately reviewed local
attestation and `--baseline` supplies the comparison artifact if policy requires
one. `--out runs/gate` saves the decision in an owned bundle.

Exit codes: PASS=0, FAIL=1, ERROR=2, REVIEW_REQUIRED=3, INCONCLUSIVE=4. Invalid input
also exits 2 with sanitized stderr. Non-PASS must never authorize automated release.
The example is syntax/code validation, not a recommended risk tolerance; synthetic
or development-only evidence cannot PASS. No deploy action exists in this repo.

Policy requires pinned subject/rubric/dataset identity, heldout human-adjudicated
cases, minimum **answered** counts in both classes, coverage and Wilson upper
bounds. Minimum answered counts conservatively also imply minimum reference counts.
Repeated families suppress independent intervals and yield INCONCLUSIVE. A trusted
expected report digest can additionally pin the precise artifact. Policies are
frozen and every decision binds the entire policy digest/revision.

Critical review, probe review and human approval are separate supplied attestations
bound to both report and policy. Verified critical false accepts fail (or demand
review per policy); unresolved critical findings demand review. Probe evidence is
required by default. Approvals never override numeric failure, missing holdout,
synthetic evidence or corrupt artifacts. There is no command-line bypass. To change
risk tolerance, the responsible human must approve and archive a new policy revision
and its rationale, identity, date, old/new digests and expected data. Reevaluate.

Attestation identifiers/digests do not authenticate people, chronology or source
truth. An independent custodian must verify and retain the actual signed review
records, source labels, probe evidence and trusted expected digests. Do not treat
self-authored JSON as human approval. This limitation prevents any claim of a
production-ready release authority; the gate is a deterministic evidence check.

Baseline comparison requires compatible judge, rubric, data/metadata, labels,
splits and adapter. The gate does not infer improvement or significance. It applies
absolute predeclared thresholds to the candidate; incompatible baselines are
INCONCLUSIVE. Injected fields such as decision=PASS are rejected by strict schema.
