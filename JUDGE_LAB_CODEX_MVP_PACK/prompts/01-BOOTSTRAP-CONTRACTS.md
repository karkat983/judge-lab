# Codex prompt 01 — package, data contracts, synthetic fixtures

## Read first
`AGENTS.md`; latest handoff; `specs/01-SCOPE-AND-NONGOALS.md`; `specs/02-ARCHITECTURE.md`; `specs/03-DATA-CONTRACTS.md`; `specs/06-SECURITY-BOUNDARIES.md`.

## Implement only this vertical slice
- Create or reconcile minimal Python>=3.12 package `judge_lab` with `pyproject.toml`, importable modules, lint/types and `pytest` config. Choose minimal reviewed dependencies; explain any new dependency.
- Implement strictly typed `Case`, `DatasetRevision`, `JudgeSpec`, `JudgeResult`, `RunManifest` (and relevant verdict enums) via validated boundary models; no provider call or dashboard.
- Implement JSONL (and optionally CSV if existing code supports it) loader and a separate **judge-facing view** that excludes reference labels, adjudication outcomes and split metadata.
- Implement stable canonical bytes+SHA-256 of input dataset/spec/rubric; reject duplicate IDs, unknown schema, invalid labels, malformed input, oversize payloads.
- Supply 8–16 explicitly SYNTHETIC controlled security-investigation cases with clear reason codes: accepted report, fabricated evidence, prohibited production action, unjustified RCA and abstention/error scenarios. Use fake organizations/services; license synthetic data explicitly.
- Write unit/security tests **before or together with implementation**. Distinguish fixtures for testing pipelines from human-adjudicated empirical benchmarks.

## Tests to require
Dataset round trip; `reference_label` absent from judge payload; duplicate IDs rejected; unsupported schema rejected; case family/split immutable; report content inert when containing instruction-like text; digest changes on tampering; cross-platform UTF-8 handling.

## Do NOT
Call model APIs; automatically label data with an LLM; seed 200 duplicated records and call them a real human-labeled benchmark; add APIs, agents, UI, stores or cloud infrastructure. Do not execute source strings.

## Output and gate
Document actual CLI/import smoke test, `pytest`, `ruff`, `mypy` outcomes, change list and limitations in `worklogs/01-contracts.md`. Stop once v1 contracts and synthetic fixtures are stable; all subsequent prompts depend on these interfaces.
