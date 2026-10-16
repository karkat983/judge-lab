# Codex prompt 04 — usable CLI, honest JSON/HTML reports

## Read first
`AGENTS.md`, `specs/02-ARCHITECTURE.md`, `specs/03-DATA-CONTRACTS.md`, `specs/04-METRICS-AND-STATISTICS.md`, `specs/08-REPORTS-AND-DECISION-GATES.md`.

## Implement
1. `judge-lab validate --judge <yaml> --data <jsonl>`: schema and permission checks, human-readable errors and nonzero exit for invalid input.
2. `judge-lab calibrate --judge <yaml> --data <jsonl> --out <dir>`: run deterministic/mock or imported predictions, produce `report.json`, `report.html`, `run_manifest.json`, optional `case_results.jsonl` with minimum safe fields.
3. `judge-lab demo`: reads bundled synthetic fixture, local mock judge, prints location of report and clear banner "synthetic demonstration, not product effectiveness evidence".
4. Python entrypoints for using normalization/metrics/report APIs without CLI.
5. Render figures, if any, from actual computed counts. Ensure HTML fully escapes untrusted text; no remote JS/CDN dependency.
6. Make report reproducibility manifest include hash-linked inputs, relevant version/seed, include exclusions/errors/unknowns. Never claim a universal "reliable" score.

## Do not implement
Cloud hosted demo, frontend SaaS, multi-tenancy, agent LLM narrative author, arbitrary cloud logs and traces, auto-labeling.

## Required tests
CLI happy path, invalid contract, missing predictor, failed judge, stdout/stderr, stable report identifiers, output collision, path traversal prevention, injection into HTML literal escaping, exact numeric agreement of HTML/JSON and case counts, secret redaction canary.

## Exit gate
A teammate can install and run demo on a clean environment with no API key; clear README commands; actual test/lint/type output recorded in `worklogs/04-cli.md`. STOP.
