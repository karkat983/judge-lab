# Phase 01 contract guide

The canonical MVP specification remains in `JUDGE_LAB_CODEX_MVP_PACK/specs/`.
This document records the implemented v1 decisions, including the details added
to complete that proposal. No legacy public import or label was changed.

## Boundaries and schemas

Use `judge_lab.serialization.decode_model(Model, utf8_json)` for external JSON.
Use `load_dataset(jsonl_path, manifest_path)` for a verified dataset snapshot.
Models are Pydantic v2, strictly typed, frozen, forbid extra fields and revalidate
instances. Collections are immutable tuples; JSON arrays become tuples without
coercing their elements. Every external Case, JudgeSpec, DatasetRevision,
JudgeResult, JudgeInput and RunManifest requires `schema_version: "1.0"`.
Nested records inherit the containing version. JSON Schema is available through
each model's `model_json_schema()`.

Direct Pydantic serialization/deserialization, `model_construct` and unvalidated
`model_copy(update=...)` are not substitutes for the external ingestion boundary.
In particular the boundary rejects duplicate JSON keys before model validation.
This is a data integrity boundary, not a sandbox against a malicious Python caller.

| Record | Key rules |
|---|---|
| Case | Required nonempty ID/family/rubric; fixed split enum; reference ACCEPT/REJECT only; `reference_frozen` must be boolean true; REJECT needs reason codes; evidence IDs unique. |
| JudgeInput | Explicit allowlist: schema/rubric revision, report, evidence, policy. No case ID/family, split, reference, reasons, adjudication or prior outcomes. |
| DatasetRevision | Source, permission/license, label protocol/provenance, UTC creation time, declared evidence status, split algorithm/seed, canonical case digest. Evidence status is a declaration, not independent certification. |
| JudgeSpec | Offline `deterministic_mock` or `imported` only; typed settings and limits; strict-label parser identifier. No new adapter executes yet. |
| JudgeResult | ACCEPT/REJECT/ABSTAIN require null error kind. ERROR requires a typed error kind. No raw output is accepted (`raw_output_ref` is null). Case/run/spec digests bind results; unknown cost is null, not automatically free. |
| RunManifest | Dataset, dataset manifest, label protocol, rubric, judge spec, splits/families, adapter version, seed, environment/package version and limits are bound to a deterministic digest. |

Case-family identity is required even for fixtures. Loader rejects duplicate IDs
and a family appearing in more than one split. Families may contain multiple cases
within one split. This is structural leakage prevention; it does not prove cases
are independently sampled or prevent a researcher from tuning on holdout data.

Missing/disputed/unlabeled references reject the entire batch with INVALID_INPUT;
there is no silent exclusion, inferred label or partial success. An adjudication
intake/exclusion workflow is deferred. CSV stays in the legacy pipeline.

## Canonicalization and provenance

JL canonical JSON v1 uses UTF-8, sorted object keys, compact separators, finite
numbers and LF-normalized strings (including CRLF/CR). Array order is preserved.
Unicode is preserved, not normalized using NFKC/NFKD. Invalid surrogates, duplicate
keys (including normalization collisions) and NaN/Infinity/overflow are rejected.
This format is **not RFC 8785**; changing its rules requires a protocol decision.

Dataset hashing sorts cases by case ID, validates IDs/family splits, and includes
full private case records, including labels and provenance fields. JSONL row order,
JSON key ordering and line-ending representation do not change identity. Semantic
changes to report/evidence/reference/policy/split do. The manifest's `sha256`
is the canonical case-array hash, not a hash of raw JSONL bytes. The full metadata
manifest is separately hashed into the run, including rights and label provenance.

`build_run_manifest` verifies the dataset first and rejects case/judge rubric
revision mismatch. Run identity includes the typed settings and environment.
`created_at_utc` is recorded but excluded from **run compatibility identity**:
re-evaluating the same frozen inputs later produces the same run ID. Phase 02
must distinguish individual attempts if needed; there is no resume store here.

Before reuse, call `require_compatible_run(stored, expected)` where `expected` is
rebuilt from trusted current inputs. Call `verify_result(result, case, run, dataset)`
to check membership and case/run/spec bindings. A digest is not a signature:
an attacker able to replace both data and all expected digests can recompute them.
Hold trusted expected manifests separately; these checks detect stale/mismatched
artifacts, not an authenticated origin or actual model execution.

## Privacy and input limits

`ContractError` exposes a fixed code, not submitted content, IDs, file paths or
validation details. Reprs omit private fields. There are no new package log calls.
`LoadedDataset.summary()` emits only schema, case count, dataset hash and declared
evidence status. It is the safe default inspection output; no reports exist yet.

`model_dump`, `canonical_bytes`, `dataset_jsonl` and `judge_input` deliberately
contain private input data. Do not log them or expose them as public reports.
Judge-facing content is still confidential; filtering reference metadata is not
PII detection or provider consent. It cannot remove a label deliberately embedded
in free-form report text by a source. No network or provider API exists in the new
package. Legacy modules retain their original privacy limitations and are not
used to persist new cases. `runs/` and `results/` are ignored by Git.

The ingestion boundary caps a dataset at 16 MiB/10,000 records, a record/manifest
at 256 KiB and nesting at 32 levels. Text fields cap at 32,768 characters; evidence
and action/reason lists at 64 entries. Input is read-only; blank records are invalid.
No arbitrary code, HTML, shell expressions, or YAML tags are executed. API callers
must use these bounded loaders for untrusted files. Serialization returns bytes;
safe output-directory/atomic-write behavior belongs to later artifact/CLI phases.

## Remaining phase gates

Phase 02 implements strict model-output parsing, mock/import adapters, normalized
result joins and execution budgets. Phase 01 validates their data contracts only.
Statistics/Wilson intervals belong to Phase 03; CLI/HTML reports to Phase 04;
baseline, probes, comparisons, gates and pilots remain unimplemented. Nothing here
asserts scientific validity, product effectiveness or release eligibility.
