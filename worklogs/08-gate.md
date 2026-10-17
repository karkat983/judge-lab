# Phase 08 — conservative deterministic CI policy

Implemented pure evaluate_gate with strict versioned YAML/JSON policy, bound human
review attestations and digest-bound decisions. CLI returns PASS=0, FAIL=1, ERROR=2,
REVIEW_REQUIRED=3, INCONCLUSIVE=4; there is no untracked override. Example offline
CI asserts the synthetic demo is INCONCLUSIVE and contains no deployment action.

Checks include trusted subject/data pins, holdout, human-adjudicated provenance,
minimum answered class counts, coverage, Wilson upper bounds, critical/probe review,
human approval record, report integrity and baseline comparability. Policy changes
invalidate old attestations. Threshold failure cannot be waived by approval text.
Docs explicitly require external authentication of reviewers and source evidence.

Actual demo gate: INCONCLUSIVE/SYNTHETIC_EVIDENCE, exit 4; JSON saved under
runs/phase08-gate. Tests cover missing holdout, synthetic/too-small evidence,
zero-error uncertainty failure, coverage vs conditional accuracy, known critical
false accept, tampering, injected PASS, absent approval, changed policy, incompatible
baseline and CLI status. Final checks: 10 gate tests passed; Ruff and mypy (16
modules) passed, all exit 0. GitHub CI definition added; remote CI not claimed run.

Limitations: records/hashes are attestations, not signatures; actual reviewers and
probe evidence must be checked by a custodian. No production authority or general
safety claim. Example thresholds are syntax, not advice. Next authorized phase:
09 local pilot toolkit; no outreach authorized or performed.
