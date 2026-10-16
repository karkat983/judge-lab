# Worklog: 01 — Bootstrap and contracts

- Date: 2026-10-17 user/session date (Asia/Kolkata).
- Task: explicit user authorization to implement Phase 01 and install local dependencies.
- Git branch/base: `main`, `475a192ed146ee6ff7b273929809eee6e0c64a4d`; no commits or destructive Git operations.
- Target gate: locally installable package, strict v1 contracts, offline fixtures, verified provenance, passing tests/lint.
- Evidence status: IMPLEMENTED for Phase 01. Empirical judge evaluation: NOT RUN.

## Requirements and scope

Read the requested audit/decision documents and canonical MVP operating documents.
The root operating/spec files were still absent at the start; canonical content is
under `JUDGE_LAB_CODEX_MVP_PACK/`. The requested `04-SECURITY-AND-PRIVACY.md` is not in
that edition; used `06-SECURITY-BOUNDARIES.md`, as required by the Phase 01 prompt.
Added root instruction/roadmap pointers without copying or overwriting the pack.
The explicit user authorization supersedes the audit's previous approval stop.

Authorized implementation includes packaging/tooling, contracts, bounded local
ingestion, canonical hashes/run compatibility, fixtures/tests and documentation.
No provider calls, new judge runner, statistics engine, release gate, hosted
service, database, probe execution, data download or Phase 02 implementation.
Network access was used only for authorized PyPI dependency/wheel downloads.

Invariants preserved:

- Existing tracked `src/*.py`, legacy tests, XSTest data, rubric/prompt,
  configuration, requirements and Git history are unchanged.
- New `judge_lab` imports never depend on the generic `src` package. Wheel discovery
  includes only `judge_lab`; legacy modules remain usable from the checkout.
- Legacy safe/unsafe labels are never mapped to new ACCEPT/REJECT references.
- References, adjudication, family/split metadata and prior outcomes are omitted
  from the explicit judge-facing view.
- No scientific results, human annotations, actual judge execution or release
  eligibility are inferred from synthetic fixtures.

## Changes made

| Files | Change and purpose |
|---|---|
| `pyproject.toml`, `requirements-dev.lock` | Python >=3.12 package, explicit discovery, minimal Pydantic runtime, separate dev/legacy extras, tested version pins, strict mypy configuration. |
| `src/judge_lab/__init__.py`, `py.typed` | Version 0.1.0 and typed package marker. |
| `src/judge_lab/contracts.py` | Frozen strict Case, JudgeInput, DatasetRevision, JudgeSpec, JudgeResult, RunManifest and nested records; sanitized ContractError; separate typed outcomes and ERROR invariants. |
| `src/judge_lab/serialization.py` | Bounded UTF-8 JSON, duplicate-key rejection, canonical LF/ordered-key serialization, finite numbers, full SHA-256 digests. |
| `src/judge_lab/load.py` | Read-only bounded JSONL/manifest ingestion, sorted IDs, duplicate and cross-split family rejection, digest verification, private default summary. |
| `src/judge_lab/provenance.py` | Deterministic run identity, complete manifest/spec/rubric/split/environment binding, compatibility and result checks. No cache or execution backend. |
| `examples/{security_fixture.jsonl,security_manifest.json,mock_judge.json,synthetic_run.json,synthetic_results.jsonl,README.md}` | Ten CC0 fictional development cases; planted reference rules; constructed ACCEPT/REJECT/ABSTAIN/ERROR examples and provenance. |
| `tests/contracts/{conftest.py,test_contracts_v1.py,test_load_and_isolation.py,test_provenance.py}` | 115 new offline test cases; socket guard; contract, parsing, leakage, immutability, privacy, Unicode, bounds and stale-artifact tests. |
| `Makefile`, `pytest.ini`, `ruff.toml`, `.github/workflows/ci.yml`, `.gitignore` | Working install/test/lint/type commands, offline pytest default, Python 3.12 lint target, CI package installation/type check, ignored generated/private artifacts. |
| `AGENTS.md`, `ROADMAP.md`, `README.md` | Canonical instruction links, current phase/status, verified Python API usage, separate legacy workflow. |
| `docs/contracts-v1.md`, `docs/dependencies.md` | Public boundary semantics, canonicalization, compatibility/privacy limits, dependency purpose/license observations. |
| `worklogs/DECISIONS.md`, this worklog | Phase 01 dispositions and actual validation evidence. Historical audit remains unchanged. |

Existing compatible code was inspected and preserved: sampling/stratification,
statistical utilities with independent kappa tests, scripted FakeLLM, retry and
rate-limiting. All their offline regression tests executed successfully. A new
isolation test directly reuses FakeLLM's call recording with an ACCEPT reply,
without invoking the legacy parser. Executing helpers are not unnecessarily
copied into contracts; runner/math integration remains in its later phase.

## Design decisions

See the Phase 01 disposition in `DECISIONS.md` and `docs/contracts-v1.md`.

1. Keep external version 1.0, complete the previously unimplemented proposal with
   required family identity, evidence status, case/run bindings and full metadata
   provenance. No released or legacy schema was changed.
2. Reject the entire dataset on a missing/disputed/unlabeled reference; no partial
   success or silent exclusion. Adjudication intake is deferred.
3. Normalize JSON arrays to tuples while strictly validating elements; require actual
   boolean true for frozen references, UTC timestamps and finite/nonnegative counts/costs.
4. Default to offline-only adapter identifiers; no executable provider integration.
   Result ERROR requires a typed error kind and cannot masquerade as a prediction.
   Raw output references are null-only; unknown estimated cost is null.
5. Run ID is a deterministic compatibility identity, excluding run creation time.
   Full dataset metadata, labels/splits, spec/settings/limits, rubric, adapter version,
   seed and environment/package version participate. Expected manifests must come
   from trusted inputs; digests are not authentication signatures.
6. Bound ingestion to 16 MiB/10,000 cases; each record to 256 KiB; depth 32; text
   fields 32,768 characters; evidence/action/reason lists 64 items.
7. Only a safe count/hash/status summary is suitable for default inspection.
   Full serialization and judge inputs remain private data; no logging/report
   implementation was added.

## Commands executed and actual results

Local interpreter: CPython **3.14.8**, macOS arm64. Development versions are pinned
in `requirements-dev.lock`. Runtime wheel smoke used a separate fresh environment.
Console output is recorded in the implementation session; wheel build output is
also in ignored `runs/phase01/wheel-build.log`.

| Command/check | Exit | Actual outcome |
|---|---:|---|
| `python3 -m venv .venv` | 0 | Created repository-local environment. |
| Initial `.venv/bin/python -m pip install ...` | 1 | Sandbox DNS could not resolve PyPI. Not a dependency compatibility failure. |
| Authorized escalated `pip install --no-cache-dir` with runtime/dev/legacy/build dependencies | 0 | Installed dependencies into `.venv`; no global installation or model SDK installation. |
| `.venv/bin/python -m pytest -q -m 'not live'` before new tests/config changes | 0 | **70 passed, 1 deselected**, 30.13s. Establishes legacy baseline. |
| `.venv/bin/python -m ruff check src/*.py tests scripts` on legacy files before new tests | 0 | All checks passed. |
| Initial whole-tree Ruff | 1 | New Python 3.12 type syntax conflicted with old py311 lint target; fixed target to py312. |
| Initial mypy | Not captured separately | Reported duplicate `src.judge_lab`/`judge_lab` resolution due to root `src/__init__.py`; command shared a shell with Ruff. Fixed explicit package bases and mypy path; final standalone result below is 0. |
| First synthetic fixture construction | 1 | Strict wrapped Pydantic validation rejected JSON arrays; explicitly froze arrays to tuples without value coercion, then fixtures generated successfully (exit 0). |
| First `pytest -q tests/contracts` | 2 | Two new test files had decorator syntax errors during collection; corrected, not legacy failures. |
| `.venv/bin/python -m pytest -q tests/contracts` after corrections | 0 | **115 passed**, 0.34s. |
| `.venv/bin/python -m pip install --no-build-isolation --no-deps -e .` | 0 | Editable package installed successfully. |
| `make test` | 0 | **185 passed, 1 deselected**, 23.87s; includes all 70 legacy and 115 new tests, including the slow bootstrap check. |
| `make lint` | 0 | Ruff: all checks passed across repository. |
| `make typecheck` | 0 | mypy: no issues in 5 new package source files. Legacy untyped code is outside strict mypy scope. |
| `.venv/bin/python -m build --wheel --no-isolation` | 0 | Built `dist/judge_lab-0.1.0-py3-none-any.whl`, containing only new package, marker and metadata. Rebuilt after README update. |
| Runtime `pip download --only-binary=:all:` into ignored local wheelhouse | 0 | Downloaded pinned Pydantic runtime wheels for clean-install check. |
| `python3 -m venv runs/phase01/wheel-venv` and its `pip install --no-index --find-links runs/phase01/wheels dist/judge_lab-0.1.0-py3-none-any.whl` | 0 | Separate environment installed the wheel and runtime dependencies without editable source access. |
| Installed-wheel Python `-I` smoke from `/private/tmp` | 0 | Loaded all ten fixtures, validated spec/run, verified all ten result bindings. Asserted `src`, pandas and pytest were unavailable and package loaded from fresh wheel environment. |
| `.venv/bin/python -m pip check` | 0 | No broken requirements. |
| `git diff --check` | 0 | No whitespace errors in tracked diff. |
| Final stdlib documentation validation | 0 | Eight changed/new Markdown files decode as UTF-8, have no trailing whitespace, and their local Markdown links resolve. |
| `git diff --exit-code -- src tests data requirements.txt config.yaml prompts` | 0 | Existing tracked implementation, tests, data and config preserved. New untracked package/tests reviewed separately. |

The final installed-wheel summary was:

```json
{"case_count": 10, "dataset_digest": "sha256:386222917fab7c3361ec6258865a707b912083b5c637d99b5eeb2b8fb9f1ba38", "evidence_status": "SYNTHETIC", "schema_version": "1.0"}
```

The one deselected test calls a live LLM. No test was omitted because it failed.
No pre-existing test or lint failure was found. Failures introduced during development
are listed above and corrected. GitHub-hosted CI and a Python 3.12 runtime were
**NOT RUN** locally; configured support/type/lint targets are not an executed CI claim.
The CLI is **NOT IMPLEMENTED** in Phase 01; the allowed import/API smoke was executed.

## Security and scientific validation

Executed negatives cover unsupported schema versions, missing fields/labels,
legacy labels, unknown/extra fields, duplicate JSON keys and case/evidence IDs,
invalid UTF-8/surrogates, malformed/deep/oversized inputs, numeric coercion,
NaN/Infinity, invalid limits, unfrozen references and contradictory policies.
Typed PARSE_ERROR/TIMEOUT/PROVIDER_ERROR/BUDGET_EXCEEDED outcomes stay ERROR.
Changing labels, content, evidence, policy, family/split, rubric, model, settings,
budget, adapter, seed, environment, label protocol, license or dataset revision
invalidates old run compatibility. Wrong case/run/spec bindings are rejected.
Secret canaries do not appear in exception formatting, reprs, logs or summaries.
Judge input isolation is tested via the existing scripted fake; instruction-like
case content stays inert. No network is permitted by the new tests' socket guard.

Ten examples are synthetic, all in development. They are not ten verified independent
incidents and do not establish a held-out population. Case 9 has constructed ABSTAIN,
case 10 constructed ERROR/PARSE_ERROR; their references remain ACCEPT. Example
latency/cost/token zeroes are test values, not observed model measurements. No model
performance, attack-success rate, customer adoption or baseline effectiveness was measured.

## Limitations and remaining risks

- Pydantic deliberately provides unsafe construction/copy escape hatches; external
  input must use the documented bounded decoding/loading API. This is not a sandbox
  against arbitrary trusted Python code mutating objects or bypassing validation.
- Digests detect stale/incompatible artifacts against trusted expected inputs, not
  malicious replacement of every input and manifest or proof of model execution.
- Metadata isolation cannot detect a reference label embedded in report text; no
  general secret/PII scanner is claimed. Full serializers must remain private.
- Legacy provider/resume/cache/raw-output limitations from the audit remain in
  the separate old workflow; Phase 01 does not adopt that persistence behavior.
- No execution-budget enforcement exists until the runner phase. No model-output
  parser, prediction import runner, metrics, HTML reports or gates are implemented.
- The version lock is not a supply-chain hash lock; cross-platform wheels/CI remain
  to be exercised. Dependency metadata licenses are recorded, not legal certification.
- The pack and audit worklogs were already untracked. New changes remain uncommitted;
  root pointers require the canonical pack to be retained when the user commits.

## Exit gate

**READY: Phase 01 definition of done met.** Package installation, strict contracts,
offline fixture validation, provenance checks, full automated tests, Ruff and strict
new-package mypy checks executed successfully. This is code/contract readiness only.

No blocking issue requires another architecture approval. Work is stopped at the
requested Phase 01 boundary. The sole next candidate, requiring a new user instruction,
is `JUDGE_LAB_CODEX_MVP_PACK/prompts/02-JUDGE-RUNNER.md`. Phase 02 was not started.
