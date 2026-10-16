# Judge Lab — audit decision register

Audit date UTC: 2026-10-16. Owner/approver: repository owner. Entries below retain their
original audit status; the Phase 01 disposition at the end records implementation
decisions taken under the user's subsequent explicit authorization. Source evidence
and checks are in `00-repo-audit.md`. PACK means `JUDGE_LAB_CODEX_MVP_PACK/`.

## ADR-001 — Resolve instruction location without overwriting the repository

- Status: PROPOSED; resolve before Phase 01 edits.
- Trigger: root AGENTS/ROADMAP/specs/audit prompt absent; PACK untracked; root README describes the old project. PACK quickstart asks to copy contents and commit, while audit prompt prohibits blind overwrite.
- Options: (A) bulk copy PACK over root; (B) retain PACK with explicit root operating links and reconcile README/roadmap; (C) selectively promote canonical documents and archive historical ones after review.
- Recommendation: B initially, with one explicit source of truth and no duplicate maintained specs. Root AGENTS should make the chosen spec precedence discoverable in future sessions. Reconcile README to distinguish implemented legacy functionality from planned MVP. Do not overwrite the README with the pack overview or automatically commit.
- Scope: root operating docs and PACK references only after approval. Audit leaves all these unchanged.
- Reason/reversibility: preserves existing instructions/history and avoids treating nested documentation as installed functionality; later relocation is reversible.
- Acceptance: root-to-canonical links resolve; future prompt paths are unambiguous; old roadmap cannot silently authorize deferred work.
- Reopen if: owner prefers selective relocation/versioning of the pack.

## ADR-002 — Add an installable package alongside legacy `src.*`

- Status: PROPOSED; Phase 01 public import decision.
- Trigger: all current code/tests use `src.*`; architecture proposes `src/judge_lab/`, Python >=3.12 and pyproject packaging.
- Options: (A) rename/move all existing files immediately; (B) coexist with an explicitly discovered `judge_lab` package and retain legacy files/tests; (C) package the generic name `src` permanently.
- Recommendation: B. Add `src/judge_lab/` and `pyproject.toml`; explicitly include `judge_lab` and its subpackages only. Do not let automatic discovery accidentally ship legacy modules. Preserve legacy checkout imports/tests. New package must not import `src.*` or depend on root working directory. Adapt reviewed algorithms/test ideas during their corresponding phases, not by sweeping relocation.
- Trade-off: temporary duplication of concepts and two test populations; avoids public import breakage and mixing label semantics. Reconsider shared private utilities only when stable common behavior justifies it.
- Scope: packaging/tooling and new contracts in 01; runner in 02; metrics in 03. No new runner shells or provider implementation in 01.
- Acceptance: fresh wheel install/import outside checkout, legacy offline tests, new tests, Ruff and mypy configured for intended scope; explicit Python floor and packaged resources.
- Reopen if: maintainers approve a breaking migration with a compatibility/deprecation plan.

## ADR-003 — Keep XSTest as legacy evidence, not the security-report baseline

- Status: PROPOSED.
- Conflict: old README/data/rubric evaluates prompt intent; PACK scope 01 requires report acceptability under independent evidence/policy constraints. Existing 200 rows and historical 30-item review do not meet new 200-family benchmark requirements.
- Options: relabel safe/unsafe as ACCEPT/REJECT; replace/delete old data; preserve old data and add distinct synthetic/demo and independently adjudicated benchmark datasets.
- Recommendation: preserve existing files/attribution; add 8–16 explicitly synthetic cases in 01. Establish a separate protocol in 05 and mark empirical B0 NOT PERFORMED until authorized independent labels exist. Do not fabricate 200 cases or claim human annotations.
- Scope: datasets, loaders, manifest provenance and README claims. Legacy ambiguous examples remain historical; new exclusions must be fixed before examining predictions.
- Acceptance: no automatic cross-domain label mapper; synthetic status survives export/reporting; insufficient empirical pool cannot become a completed benchmark; family-disjoint splits.
- Reopen if: a rights-cleared report dataset and independent adjudication become available.

## ADR-004 — Separate prediction outcomes from release decisions

- Status: PROPOSED; contract freeze in 01, parser implementation in 02.
- Conflicts: `src/verdict.py` uses safe/unsafe/invalid; archive line 132 proposes judge PASS/FAIL/ABSTAIN/INVALID_INPUT/ERROR; archive line 433 shows SAFE/UNSAFE/ABSTAIN. New spec 03 defines reference ACCEPT/REJECT, prediction ACCEPT/REJECT/ABSTAIN, system ERROR, and separate gate statuses.
- Options: permissive aliases/word extraction; reuse old enum; implement distinct strict v1 contracts while retaining legacy behavior separately.
- Recommendation: distinct contracts. ERROR requires typed system failure metadata, never a model verdict or reference. PASS/FAIL/REVIEW_REQUIRED/INCONCLUSIVE/ERROR belong to deterministic gate output only. No fallback from malformed prose or invalid JSON to a valid label. Legacy parser tests continue under old workflow.
- Evidence: audit reproduced invalid JSON verdict with reason safe becoming safe, and contradictory JSON objects taking first verdict.
- Acceptance: label-only contamination/unknown-label tests, ERROR invariants, no judge-generated gate authority; unsupported external versions rejected.
- Reopen if: a specific external format requires an explicit versioned converter with lossless semantics.

## ADR-005 — Reuse mechanisms only after integrity/privacy/budget hardening

- Status: PROPOSED; requirements established in 01–02, report checks in 04.
- Trigger: raw replies saved; results not ignored; resume keyed by ID; cache ignores host/wrapped identity; unknown model cost zero; default provider live-capable.
- Options: reuse wrappers/store unchanged; replace entire legacy project; preserve old code while building minimal safe artifacts/runner for new contract.
- Recommendation: third option. Default mock/import, full canonical digests binding dataset/labels/splits/rubric/spec/adapter; exact ID joins; reject mixed/duplicate/stale results. Minimized output with redacted-or-none raw reference, explicit output directory and overwrite controls; atomic UTF-8 writes. Add `runs/` and sensitive legacy result exclusion in reviewed metadata change. No shared persistent cache or threading unless needed.
- Future provider work: explicit consent, destination/model visibility, bounded call/time/cost accounting including attempts. Unknown pricing is unknown, not zero; current hard-coded model/API/rate claims remain unverified.
- Acceptance: no default network calls; stale-result/host-identity tests; limits and typed errors; secret canary/HTML/path/overwrite tests before sensitive use.
- Reopen if: repeat-run measurements justify cache/concurrency complexity or a pilot explicitly needs live integration.

## ADR-006 — Adopt explicit denominators and undefined statistics

- Status: PROPOSED; implement only in Phase 03.
- Conflict: legacy `accuracy` excludes invalid predictions, while new spec 04 distinguishes conditional accuracy, overall-case correctness, coverage and per-class abstain/error counts. Bootstrap kappa does not replace Wilson intervals for proportions.
- Options: wrap old Agreement unchanged; rewrite everything without reference tests; adapt validated formulas and independent old goldens to explicit new outputs.
- Recommendation: third option. Preserve old stats for old task; implement 2x2 answered counts plus abstain/error counts, false accept = reference REJECT/prediction ACCEPT, explicit denominators, null plus reason for undefined values, Wilson 95%. Initial kappa point estimate is sufficient; retain legacy bootstrap as historical functionality until clustered-resampling assumptions are justified.
- Scope: metrics/report contracts, comparison and gate semantics. Do not translate zero sample size to zero risk or 100% agreement to universal safety.
- Acceptance: spec 04's four goldens, empty/all-abstain/error/one-class cases, zero errors in 20 still nonzero Wilson upper bound, JSON rejects NaN/Infinity, family correlation disclosed.
- Reopen if: approved experimental design supplies defensible resampling/weighting requirements.

## ADR-007 — Retire old expansion as an active work queue

- Status: PROPOSED; current audit already follows explicit user MVP scope.
- Conflict: locally ignored `docs/commit-plan.md` calls for a next live run, bias/ensemble work and 250 commits; archive lines 257–291 proposes ten agent roles and broader capabilities; current PACK says zero runtime agents and prompts 01–10 in order.
- Recommendation: preserve historical files; label/link them as historical during approved doc reconciliation. Defer ensembles, pairwise extensions, generalized trajectories, adaptive attack agents, hosted dashboard, multi-tenancy, cloud integration and certification. Development assistance is not a runtime product feature. No live calls merely to claim curriculum coverage.
- Alternatives rejected: deleting history; completing all legacy checkboxes; building generic shells for future agents.
- Acceptance: only current prompt's files/features change; no product agent orchestration; scoped claims with no certified-safe terminology; no invented pilot/competitor evidence.
- Reopen if: completed empirical gates and explicit human approval support a specific expansion.

## ADR-008 — Resolve ambiguities within the MVP proposal before freezing contracts

- Status: PROPOSED; Phase 01 items below require decisions before public v1 schema freeze; later-phase decisions may wait for their gate.
- Options: silently invent fields/precedence; follow examples literally despite prose requirements; document explicit interpretations with acceptance tests.
- Recommendation: explicit interpretations, reviewed at the relevant gate:

| Ambiguity / sources | Proposed minimal resolution | Gate / oracle |
|---|---|---|
| Case example in spec 03 lacks `case_family_id`, severity and defect type, but prompts 01/05 and specs 04/07 require family immutability/splits/slices. | Add explicit family identity (required for empirical split claims); define optional authoritative slice metadata and unknown values. Never use row ID as proof of independent family. | 01 contract review; 05 disjointness tests. |
| Spec 03 says reject undefined/missing labels, but also says missing label must exclude/report; scope allows disputed/unlabeled adjudication records. | Strict core Case requires ACCEPT/REJECT. A separate intake/adjudication exclusion record represents missing/disputed labels with reason/count; no silent dropping or inferred label. Explicitly decide whether mixed imports fail as a batch or return a validated dataset plus exclusions. | Resolve mixed-import policy in 01; tests before loader contract freeze. |
| Architecture signature takes Case while prose and prompt 02 require a blind judge view. | Typed judge-facing view only; allowlist fields. Keep references, reference reason codes, adjudication, split and oracle outcomes outside it. | 01 leakage tests; 02 protocol test. |
| Spec 03 probe example mutates `authoritative_evidence[0].text`; spec 05 says authoritative independent facts must remain protected. | Distinguish an explicitly designated lower-trust quoted/log field from immutable authoritative facts and reference record. Reject probes until field control and preservation can be independently established. | Model trust separation in 01; finalize manifest/oracle in 06. |
| Spec 03 report keys include `counts/denominators/slice_breakdowns/evidence_manifest`; spec 08 uses `population/provenance/slice_metrics/decision`. | One canonical machine schema with all required information, explicit mapping for human views; do not maintain competing numerical copies. Gate output remains separate/optional. | 03–04 schema review and JSON/HTML agreement. |
| Spec 08 describes too-wide uncertainty as INCONCLUSIVE; prompt 08 explicitly tests Wilson upper exceeding limit as FAIL. | Validate integrity first; inadequate required evidence => INCONCLUSIVE; sufficiently eligible evidence violating a declared bound policy => FAIL. Resolve thresholds and precedence explicitly; do not weaken policy to pass. | 08 reviewed truth table and fail-safe tests. |
| Spec 08 permits logged override, while prompt 08 asks to document authorization and forbids untracked bypass. | Document manual workflow, no runtime bypass initially; machine non-PASS remains nonzero. | 08 CLI tests. |

- Scope/reversibility: these are proposals for design completion, not schema changes made in the audit. Review before publishing v1; later incompatible changes need version bump/ADR.
- Reopen if: validated pilot workflows reveal a need for a different intake, metadata, probe or gate contract.

## Review request and stop boundary

Review ADR-001 through ADR-004 and the Phase 01 rows of ADR-008 before implementation. ADR-005/006 constrain subsequent runner/math work; other unresolved choices remain explicit gates. Proposed reusable material and per-file sequence are in the audit.

The user explicitly requested stopping after the audit. PACK `prompts/00-REPO-AUDIT.md` also says: **"Exit gate: human can approve exactly which existing modules to reuse and which proposed changes to make. Stop after presenting actual findings."**

At the audit gate, no implementation was authorized. That historical stop was
superseded by the user's explicit Phase 01 authorization, recorded below.

## Phase 01 disposition — 2026-10-17 user authorization

The user explicitly authorized implementation, environment/dependency setup,
reasonable compatible design decisions, and tests, without another architecture
approval. This is authorization to implement Phase 01, not blanket approval of
every later-phase ADR. No public legacy contract was changed.

| ADR | Phase 01 disposition |
|---|---|
| 001 | Implemented root AGENTS/ROADMAP pointers; canonical specs remain in PACK. Missing requested `04-SECURITY-AND-PRIVACY.md` resolved to actual spec 06. README distinguishes legacy and new status. |
| 002 | Implemented installable `src/judge_lab`, explicit discovery, runtime/dev/legacy extras and pinned development environment. Legacy modules unchanged. mypy uses explicit package bases to avoid treating the new package as `src.judge_lab`. |
| 003 | Preserved XSTest; added ten CC0 synthetic development fixtures with planted defects and no human-adjudication claim. |
| 004 | Implemented strict literal types for separate references, predictions, system errors and result invariants. No gate enum implementation or model-output parser yet; those remain future phases. |
| 005 | Implemented canonical hashes, full run compatibility identity, result bindings, private model reprs/sanitized errors/safe dataset summaries and ignored output paths. No new cache, resume store, model runner or live provider. |
| 006 | Deferred metrics implementation; original statistics code and independent tests preserved and executed. |
| 007 | Followed MVP scope. No agents, ensembles, generic platform, claims of superiority or live calls. |
| 008 | Required family ID; whole-dataset rejection for missing/disputed labels; explicit judge view; typed settings/limits; source/rights/label-protocol manifest in run identity. Further probe/report/gate questions remain pending. |

### Contract details chosen during implementation

- `schema_version` is mandatory on external records, with nested structures governed
  by the parent version. Extra keys, invalid Unicode, duplicate keys, unsupported
  versions, nonfinite numbers and type coercions are rejected at ingestion.
- JSON arrays become immutable tuples. UTC ISO timestamps are parsed explicitly;
  non-UTC/naive dates are rejected. Frozen reference must be actual boolean true.
- `DatasetRevision` stays a metadata manifest. `LoadedDataset` combines that manifest
  with immutable cases. JSONL-only ingestion is deliberate; no incompatible CSV mapping.
- `JudgeResult` additionally requires `case_digest` and `run_id`; RunManifest also
  binds dataset metadata and label protocol. These complete the previously unimplemented
  v1 proposal, rather than changing a released schema. `raw_output_ref` is null-only
  in Phase 01; unknown costs can be null. Future raw artifact support needs review.
- Run ID represents compatibility, not a unique attempt. It excludes run timestamp
  and includes all configuration/environment/provenance inputs. Expected manifests
  must be built from trusted inputs; digests are not signatures.
- No label metadata or case/family ID enters JudgeInput. Authorized report/evidence
  text remains visible and may be confidential; label isolation is not PII detection.
- Existing fake LLM behavior is reused in isolation tests. Sampling/statistical/retry/
  rate-limit helpers remain intact and tested; new execution/math wiring is deferred.
- Worklog filename follows the user's explicit request,
  `worklogs/01-bootstrap-contracts.md`, rather than the pack's shorter `01-contracts.md`.

Remaining public-contract choices for phases 02–08 (probe trust surfaces, report
field mapping, gate uncertainty/override semantics) are not silently resolved here.
The subsequent user instruction authorizes phases 02–10, sequential checks,
commits/pushes and removal of confirmed obsolete/generated files. Per-phase approval
pauses are superseded; human annotations, pilot participation and independent
review cannot be supplied by authorization alone. Preserve reusable legacy code;
remove only confirmed redundant/generated material and record cleanup separately.
