# Synthetic Phase 01 fixtures

All files here are original fictional test data dedicated to the public domain
under **CC0-1.0**. They contain no employer telemetry, credentials or human interviews.
The code remains MIT licensed. No actual judge or human annotation campaign produced
these outputs, and they are not a 200-case empirical baseline.

- `security_fixture.jsonl`: ten development cases; five ACCEPT and five REJECT.
  Rejection defects are planted: fabricated evidence, prohibited actions,
  unsupported root cause and missing required evidence. References come from
  these deliberately constructed rules, not a model's assessment of the cases.
- `security_manifest.json`: source/permission/label protocol and canonical dataset digest.
- `mock_judge.json`: offline judge specification for validating contracts. The adapter
  name reserves Phase 02's interface; there is no new mock runner in Phase 01.
- `synthetic_run.json`: bound example manifest with deliberately declared fixture
  environment `python=3.12`, `platform=synthetic-fixture`. This is not a measured run.
- `synthetic_results.jsonl`: constructed contract examples. Cases 9 and 10 have
  valid ACCEPT references but illustrative ABSTAIN and ERROR/PARSE_ERROR outcomes.
  All timing/token/cost values are placeholder zeroes for these synthetic examples.

`adjudication_id=synthetic-*` identifies the fixture record, not a human adjudicator.
All cases are development-only. Family IDs do not establish statistical independence.
Instruction-like text is inert data; no probe execution or attack-success claim is made.

Digests can be recomputed using `dataset_digest`, `digest` and `build_run_manifest`.
If fixture content changes, regenerate its manifest and bound examples together;
tests reject inconsistent artifacts. LF/CRLF formatting and JSON key order are canonicalized.
