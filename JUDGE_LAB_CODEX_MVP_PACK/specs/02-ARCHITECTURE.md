# 02 — Local-first architecture and module boundaries

## Workflow diagram
```
                 read-only controlled inputs
  judge.yaml   dataset.jsonl    predictions?    probe_manifest?
      │              │               │               │
      └──────────────┴───────────────┴───────────────┘
                             ▼
              VALIDATE + SNAPSHOT + HASH
                             │
                    RUN / IMPORT JUDGE
                 (mock default, opt-in live)
                             │
                     STRICT VERDICTS
                             │
                   ┌─────────┴─────────┐
                   ▼                   ▼
           CALIBRATION METRICS     CONTROLLED PROBES
               + UNCERTAINTY      + VALIDITY ORACLES
                   └─────────┬─────────┘
                             ▼
                EVIDENCE-BOUND REPORT
                             │
                  OPTIONAL STATIC POLICY
                   PASS / FAIL / REVIEW /
                   INCONCLUSIVE / ERROR
```

No orchestration LLM, agent memory, graph DB, orchestration server, hosted worker, GPU, or telemetry ingestion is necessary.

## Proposed package tree
```
judge-lab/
  AGENTS.md
  docs/                         # this guide, if relocated
  pyproject.toml
  src/judge_lab/
    __init__.py
    cli.py
    contracts.py                # typed schema definitions and strict validation
    load.py                     # JSONL / CSV, deterministic ordering
    provenance.py               # digests, hashes, manifests
    judges/
      base.py                   # protocol interface
      mock.py                   # deterministic offline
      imported.py               # predictions with case-id join
      provider_optional.py      # separately gated
    metrics/
      binary.py                 # confusion, coverage, kappa
      uncertainty.py            # Wilson 95% etc
    probes/
      manifests.py
      validity.py               # deterministic allowable mutations
      evaluate.py
    reports/
      json_report.py
      html_report.py
    gates/
      policy.py                 # immutable policy evaluation
  examples/
    security_fixture.jsonl
    mock_judge.yaml
    sample_policy.yaml
  tests/
    unit/
    integration/
    security/
    goldens/
  worklogs/
  runs/                          # gitignored, possibly sensitive
```
File names are suggestions; reconcile with existing code during repo audit. Avoid creating empty framework shells for phases not yet authorized.

## Important interfaces
- `JudgeAdapter.evaluate(case: Case, spec: JudgeSpec) -> JudgeResult` (sync initially).
- `load_dataset(path) -> DatasetRevision` with per-record validation and digest.
- `calibrate(cases, predictions, protocol) -> CalibrationReport` pure function.
- `run_probe(manifest, judge, oracle) -> ProbeRunReport` only on validated controlled inputs.
- `evaluate_gate(report, policy) -> GateDecision` pure function, no live judge call.

## Versioning and immutability
Freeze `dataset_digest`, `label_protocol_revision`, `rubric_digest`, `judge_spec_digest`, `split_digest`, `run_seed` and `adapter_version` in each report. Hash canonical serialized bytes for reproducibility; normalize line endings and use deterministic JSON field ordering. Keep labels separate from judge-visible candidate fields; prevent any path that exposes reference labels to model prompts in blind tests.

## Runtime safety
- Local files as the default; no SQLite until artifacts require it; no distributed service.
- Avoid network by default; optional provider adapter requires explicit opt-in and budget/time cap.
- Filesystem writes are restricted to caller-chosen output dir. Use atomic writes. Don't overwrite existing run output without explicit flag.
- UI HTML must escape untrusted case text; preferably show shortened/redacted snippets or IDs.
- Explicit structured errors (`INVALID_INPUT`, `PARSE_ERROR`, `TIMEOUT`, `PROVIDER_ERROR`) do not become `REJECT` or `ACCEPT`.

## Why no product agents initially?
Nothing in the initial experiment requires autonomous reasoning. Deterministic metrics and fixed probes are easier to verify. An LLM-based attack generator might be evaluated later against non-agentic alternatives, but it cannot generate its own ground truth or validate its own wins.
