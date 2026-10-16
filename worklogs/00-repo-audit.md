# Worklog: 00 — Repository audit

- Date UTC: 2026-10-16; diagnostic timestamp 18:14:15 UTC.
- Task: audit only, requested by the user; no implementation authorized.
- Git: `main`, HEAD `475a192ed146ee6ff7b273929809eee6e0c64a4d` (Parallel judging with a thread pool). Local status reports `main...origin/main`; no remote fetch performed.
- Target gate: human review of reuse decisions and migration sequence before Phase 01.
- Evidence status: audit IMPLEMENTED; existing implementation PARTIAL; full test/lint execution BLOCKED by missing dependencies.

## Requirements and scope

Authorized deliverables are this file and `worklogs/DECISIONS.md`. Existing code, tests, data, configuration, documentation and Git history are preserved. No dependencies installed, model calls made, data downloaded, production systems accessed, files deleted, or implementation started. Python imports may create ignored bytecode cache files; subsequent diagnostics disabled bytecode writes.

The requested root `AGENTS.md`, `ROADMAP.md`, `specs/`, and audit prompt do not exist at those root paths. The supplied instructions live under `JUDGE_LAB_CODEX_MVP_PACK/` (abbreviated **PACK** below). Read the eight requested documents completely from PACK, plus the actual root README. Also read all existing source, tests, scripts, root configuration, legacy docs/data documentation, PACK specs 04–10, prompts 01–10, quickstart and handoff/ADR templates. Inspected relevant archived blueprint sections; did not treat the archive as implementation authority. Read the entire attached AI Engineer curriculum.

Use the user-selected PACK MVP scope for this audit, without moving or adopting files into the root automatically. No old root AGENTS conflict exists because that file is absent. PACK's quickstart copy/commit directions do not authorize overwriting the existing README during this audit.

Test oracle: existing offline tests and lint, independently checked local artifact hashes/sample reconstruction, fake-judge smoke check, and bounded read-only diagnostics. Distinguish inspection findings from executed checks and unit tests from scientific validation.

## Current state and inventory

The repository is an existing XSTest **prompt-safety classification** experiment. The new MVP is a **security-investigation report evaluator calibration** tool. These have reusable engineering and mathematics, but different populations, labels, rubrics and acceptance criteria. Renaming the old labels cannot produce the new benchmark.

Initial Git state: 52 tracked files, no tracked modifications, and untracked `.DS_Store` plus the 41-file PACK. `docs/commit-plan.md` exists locally but is ignored by `.git/info/exclude:7`; it is absent from `git ls-files` and a normal fresh clone. `data/raw/xstest_prompts.csv` is present locally and ignored. `.venv` is absent. `results/` exists and is empty. No prior worklogs exist.

Legend: EXISTS means present, not necessarily verified correct; PARTIAL means useful existing behavior falls short of the new contract; PLANNED means absent but authorized by a later prompt; DEFERRED means outside current MVP; CONFLICTING means incompatible with the new contract.

| Area / files | Status | Observed behavior and disposition |
|---|---|---|
| Root `README.md`, `docs/rubric.md`, `prompts/judge_v1.txt` | CONFLICTING | Describe safe/unsafe request classification. README still calls the judge planned although runner code exists. Preserve and reconcile later. |
| PACK operating docs and `ROADMAP.md` | EXISTS | Instruction pack, not implemented capability; untracked and nested. |
| `docs/commit-plan.md` | CONFLICTING | Locally ignored 250-commit plan; ticks 001–047, then live experiments, bias, ensembles. It is historical, not the active work queue. |
| PACK archived blueprint | DEFERRED | Ten logical agent roles, trajectory/state evaluation, cross-domain packs, control plane and certification language are not MVP requirements. |
| `src/__init__.py`, 15 other `src/*.py` | PARTIAL | Imports use `src.*`; no installable `judge_lab` package, `pyproject.toml`, entrypoint or declared Python minimum. |
| `src/config.py`, `config.yaml`, `.env.example` | PARTIAL | YAML loading and repository-relative paths; default live Ollama client, optional Anthropic. No validated v1 configuration or explicit live-consent gate. |
| `src/data.py` | PARTIAL | CSV columns/labels/duplicate IDs/empty text validation; no Case/DatasetRevision schema, JSONL loader, size limits, provenance or explicit exclusion protocol. Blank ID validation missing. |
| `src/sample.py`, `scripts/fetch_data.py` | PARTIAL | Seeded stratification, dedup and download script. Sampling reproduced offline; no incident-family splits, label freeze or insufficient-pool refusal. |
| `data/prompts.csv`, `data/SOURCE.md`, `data/DATA_CARD.md`, `docs/data.md`, `docs/label_review.md` | EXISTS | Documented XSTest sample and historical 30-item review; not a security-report dataset. Retain source/license attribution. |
| `src/verdict.py`, `src/parse.py` | CONFLICTING | `safe/unsafe/invalid`, JSON extraction and word fallback; incompatible with strict `ACCEPT/REJECT/ABSTAIN` and typed system ERROR. |
| `src/fake_llm.py`, `src/llm.py` | PARTIAL | Scripted offline fake and provider clients; no judge-facing Case view or v1 adapter/result contract. Provider claims unverified. |
| `src/judge.py`, `src/store.py` | PARTIAL | Sequential/parallel judging, JSONL append and resume. No validated prediction import, run identity, bounded run or safe artifact protocol. |
| `src/prompts.py`, `src/cache.py` | PARTIAL | Prompt hashing and response cache; 12-character prompt hash, incomplete cache identity, no full run/evidence provenance. |
| `src/retry.py`, `src/ratelimit.py`, `src/usage.py` | PARTIAL | Retry, request spacing and accounting helpers. No enforced global call/time/cost budget; unknown models cost zero. |
| `src/stats.py` | PARTIAL | Confusion, accuracy, kappa, unsafe-class measures and percentile bootstrap. Missing new denominator/error semantics, Wilson intervals and JSON-safe undefined results. |
| `tests/` | EXISTS | 16 test modules, 62 statically counted test functions, plus conftest/init. Parameterization means this is not a collected test count. Full execution blocked. |
| `requirements.txt`, `pytest.ini`, `ruff.toml`, `Makefile`, `.github/workflows/ci.yml` | PARTIAL | Pytest/Ruff and offline CI configured; no mypy config. Requirements use lower bounds; Ruff targets 3.11, CI 3.12, available interpreter 3.14.8. |
| Strict schemas, full digest manifests, separated judge input | PLANNED | Prompt 01. |
| Normalized prediction import and bounded offline runner | PLANNED | Prompt 02. |
| Wilson/coverage/false-accept metrics and null semantics | PLANNED | Prompt 03. |
| CLI, JSON/escaped self-contained HTML reports | PLANNED | Prompt 04; no current CLI to demonstrate. |
| Independent 200-family security baseline | PLANNED | Prompt 05; qualifying labels and frozen splits absent. |
| Controlled probes / independent validity oracle | PLANNED | Prompt 06; no implemented bias or attack experiments. |
| Matched-budget held-out comparison | PLANNED | Prompt 07; no empirical results. |
| Deterministic release gate | PLANNED | Prompt 08; existing CI is code checks only. |
| Pilot toolkit and independent review | PLANNED | Prompts 09–10; zero pilot/reviewer evidence found. |
| Ensembles, pairwise experiments, runtime agents, hosted platform | DEFERRED | Preserve plans, do not build from legacy roadmap. |

Dependency inventory: pandas, scikit-learn, matplotlib, PyYAML, python-dotenv, pytest, Ruff, Anthropic are in requirements. NumPy is imported directly but only transitively installed. Anthropic is described as optional but installed unconditionally by requirements. Matplotlib and dotenv have no use in inspected source. Project license is MIT; local data documents CC BY 4.0. Dependency license/version inventory remains a bootstrap task; no license audit or external provider capability verification is claimed.

## Changes made

| File | Change | Why |
|---|---|---|
| `worklogs/00-repo-audit.md` | Created | Inventory, actual diagnostics, risks, phase sequence and curriculum mapping. |
| `worklogs/DECISIONS.md` | Created | Reviewable ADR candidates; none represented as human-approved. |

## Commands actually executed and results

Commands ran from repository root. Failed tool startup is not a failing application test and not a test pass.

| Command/check | Exit code | Observed result |
|---|---:|---|
| `git status --short --branch`, `git ls-files`, `git log -5 --oneline`, `git rev-parse HEAD`, `git diff --stat` | 0 | Initial state above; no tracked diff. |
| Initial `cat` of requested root files | 1 | Root README read; missing operating docs located in PACK and then read fully. |
| `python3 --version` | 0 | Python 3.14.8. |
| `python3 -m pytest -q -m 'not live'` | 1 | `No module named pytest`; no tests collected or executed. |
| `python3 -m ruff check .` | 1 | `No module named ruff`; lint did not execute. |
| `make test` | 2 | `.venv/bin/python` absent; recipe reports Error 127. |
| `make lint` | 2 | `.venv/bin/python` absent; recipe reports Error 1. |
| `python3 - <<'PY'` read-only stdlib diagnostics (details below) | 0 | Parsed 35 Python files; verified hashes/sample; fake judge smoke; parser probes. |
| `PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'` synthetic diagnostics (details below) | 0 | Resume/cache identity/cost observations reproduced; no model/network calls or artifact writes. |
| Final `git diff --check`, `git diff --exit-code`, `git status --short`, stdlib document checks | 0 | No tracked changes; only new `worklogs/` alongside initial untracked files. Both worklogs decode as UTF-8, have no trailing whitespace and have balanced code fences; PACK count verified as 41. |
| `mypy src` | NOT RUN | Not configured, declared or installed. |
| Unfiltered `pytest` / live marked test | NOT RUN | One live test calls configured provider; audit forbids model calls. README's bare `pytest` does not exclude it. |
| `judge-lab` CLI demo / fresh-install check | NOT RUN | No package entrypoint; no install performed in audit. |
| Fetch, live experiment, empirical baseline, probes, gates, pilots | NOT RUN | Outside audit scope; new capabilities/data absent. |

Audit discovery also encountered a zsh unmatched-glob error while searching for alternate interpreters; no alternate runtime was used. Missing modules were checked using `importlib.util.find_spec`: pytest, Ruff, mypy, pandas, NumPy, sklearn, YAML and Anthropic were all absent. Existing cache directories do not prove current tests passed.

The two inline diagnostics used existing modules and stdlib only; their source/results are in the task transcript. Reproduction recipe:

1. Parse `src/*.py`, `tests/*.py`, `scripts/*.py` with `ast.parse`: 35 files parse successfully. Syntax parsing does not validate imports or types.
2. Read both CSVs with `csv.DictReader`; hash original bytes with SHA-256. Transform raw rows exactly as `scripts/fetch_data.py:to_row`, deduplicate, call existing `stratified_sample(rows, 200, 'category', 13)`, sort by ID, compare entire row dictionaries against committed CSV. Assertion passed.
3. `Judge(FakeLLM(default='{"verdict":"safe"}')).judge('audit-smoke', 'How do I kill a Python process?')` returned safe; one fake call recorded.
4. Call `parse_verdict` with the inputs in the findings below; record actual outcomes.
5. Create a fake old safe Judgment for `same-id`, patch `src.store.read` in memory to return its record, then call `judge_all` with the same ID, changed content and a new fake returning unsafe. Observed safe, zero new calls. The patched read plus full cache hit means no output file was created.
6. Compare `CachedClient.identity()` for same model/options but two local host strings, with environment cleared in the test context. They are equal. No `complete()` call. Two differently scripted FakeLLMs wrapped in MeteredClient also have equal identities.
7. `ModelUsage(input_tokens=1000000).cost_usd('unpriced-remote')` returned `0.0`.

## Measurements and scientific limits

| Artifact | Measured value |
|---|---|
| Committed sample | 200 rows; 200 unique IDs; 110 safe, 90 unsafe; 18 categories. |
| Sample SHA-256 | `26a58bb74af52deb9f703129036a37e0f2bdbd4cc2cb81472d2c5aba86d9efd4` (matches docs). |
| Local raw SHA-256 | `11783fb294ed017473ee53c207d71f2161c7672c8d0b037501e78387f801cb5a` (matches docs); 450 rows. |
| Reconstructed sample | Exact equality to committed CSV; zero raw duplicates under existing normalization. |
| Security-investigation independent benchmark families | None available in inspected repository; cannot infer independence from unique XSTest IDs. |
| Empirical judge metrics / adversarial variants / users | Not measured; no results artifacts or pilot evidence found. |

The 28 agreements / 2 ambiguous cases / 0 clear disagreements among 30 reviewed prompts are **historical documentation**, not annotations performed or independently verified in this audit. The current loader/stats do not implement the documented special ambiguity treatment. There is no frozen incident-family holdout, matched-cost study, or independently adjudicated security-report pool. The sample's documented origin and checksums do not establish suitability for the new task. No claims about current vendor features, prices, curriculum salary outcomes, or scientific superiority are made; no web research was needed for the local audit. PACK spec 09 competitor matrix remains UNVERIFIED, to be researched in prompt 07.

## Findings and risks

| Priority | Finding and evidence | Required disposition |
|---|---|---|
| High | **Task/label mismatch.** `src/verdict.py:4`, old rubric and data describe request safety, not report acceptability. Archive also mixes judge PASS/FAIL and SAFE/UNSAFE. | Separate new contract; no silent label conversion or XSTest baseline substitution. ADR-003/004. |
| High | **Permissive parser can promote invalid output.** `src/parse.py:24–53`: `{"verdict":"maybe","reason":"safe"}` returned safe; two contradictory JSON verdicts returned first safe. ACCEPT, REJECT, ABSTAIN all returned invalid. | Preserve legacy tests; new strict parser with contamination tests in 02. |
| High | **Stale resumed evidence.** `src/judge.py:44–48,70`: IDs alone decide reuse, ignoring changed content/model/prompt. Reproduced safe output with changed content and zero new calls. `tests/test_store.py` currently expects reuse after changing fake output. | Bind reuse/import to validated run and input digests; reject duplicates and mixed runs. |
| High | **Raw-output privacy exposure.** `src/judge.py:15`, `src/store.py:9–20`, `src/cache.py:47` persist raw replies; no redaction or opt-in. `.gitignore` omits `results/` and future `runs/`. | Minimize new artifacts and ignore run directories in reviewed bootstrap; test redaction before real data. No actual secret leak discovered. |
| High | **No enforced offline consent or run budget.** Default `make_client` is Ollama; environment can redirect host; request timeout is 600s. Retry limits individual attempts, not total calls/time/cost. Meter counts successful replies only. | Default new mock/import; opt-in provider and bounded accounting only later. |
| High | **Label leakage prevention unproven.** Existing Judge takes only ID/text, so no direct label forwarding was found. New structured Case risks serializing references, reasons, splits and adjudication fields unless isolated. | Explicit allowlisted judge view and negative serialization tests in 01. |
| High | **Statistical contract gaps.** `src/stats.py:33–50` drops invalids from accuracy, raises when none answered, lacks coverage/Wilson and reference validation. All-one-class kappa has no null guard; bootstrap has no empty-resample guard (`:68–77`). | New goldens and denominator/null contract in 03. Undefined-statistic observations here are source inspection, not executed NumPy/sklearn results. |
| Medium | **Cache identity incomplete.** `src/cache.py:28–33` ignores provider host, underlying wrapped class/version and fake rules; equal identities reproduced. Same-key writes share a `.tmp` path (`:46`). | Keep hash idea, redesign identity and concurrency handling before reuse; concurrency race is inspection risk, not reproduced. |
| Medium | **Unpriced usage becomes free.** `src/usage.py:25–27` returns zero for unknown remote model. Static rates and provider API assumptions lack provenance. | Unknown cost must remain unknown and prevent unsupported budget PASS; verify provider facts only when adapter work is authorized. |
| Medium | **Validation, paths and encoding incomplete.** `src/prompts.py:9` allows unsanitized names into path; loaders/store have no payload bounds or schema versions; several text reads/writes lack explicit UTF-8; store is append-only without integrity checks. | Boundary tests and controlled paths/atomic output. No path exploit executed. |
| Medium | **Reproducibility and dependency gaps.** No venv/lock/installable package/types; raw source fetch is mutable upstream, although local checksums match; lower-bound dependency specs may drift. | Review minimal dependency/pinning strategy; keep offline raw-file absence explicit. |
| Medium | **Sampling does not establish family independence.** Existing sampler depends on input ordering and caps n to pool size. ASCII-only dedup normalization can collapse distinct Unicode strings. | Freeze ordered source and family splits; refuse fabricated 200-case evidence; retain legacy behavior separately. |
| High for claims | **Unvalidated assurance language.** Archive line 70 proposes judge certification; its sections 15/21 propose agents and incompatible enums. Root README has no numbers; no basis for scientific readiness or market claims. | Use scoped reliability-report terminology and explicit NOT PERFORMED/INCONCLUSIVE. |

Missing tests for the new contract include reference/split leakage, invalid/oversized inputs, strict verdict contamination, full provenance, mixed-run imports, all-abstain/error/undefined statistics, Wilson limits, family separation, oracle independence, budget caps, HTML escaping, secret canaries, traversal/overwrite, conservative gates and pilot counting. Existing tests cover old loader negatives, parser shapes, fake judge, ordering/resume, caching, retry/rate limiting, sampling, cost arithmetic and independent kappa examples. Their presence is useful; their runtime pass status remains unknown.

## Reuse proposal for review

- **Preserve unchanged as legacy:** all current `src/*.py`, existing tests, XSTest data/rubric/prompt and historical docs. Keep old workflow runnable when dependencies are available.
- **Adapt concepts and tests in appropriate phases:** scripted fake/call recording; deterministic stratification/allocation; retry and rate-limiter test patterns; content-hash approach; hand-computed confusion/kappa tests. Adaptation does not imply importing the old verdict semantics into the new package.
- **Redesign before reuse:** parser/verdicts, schemas/loader, stats outputs/denominators, run/resume/store, cache identity and cost/budget behavior.
- **Defer:** live provider integration, threading, generic caches if unnecessary, pairwise judging, ensembles, runtime agents, platform infrastructure. No deletion proposed.

Proposed package strategy: add installable `src/judge_lab/` with explicit package discovery and Python >=3.12; preserve root `src` legacy imports and tests from repository checkout. New package must not depend on ambiguous `src.*` imports. Adopt only necessary implementations behind reviewed v1 interfaces. See ADR-002 for alternatives and wheel/fresh-install checks.

## Minimal file-level sequence (proposal, not authorization)

All prompt filenames below resolve under PACK `prompts/`. Estimates are engineering working days, not commitments, and exclude external labeling, pilot recruitment and review waiting time. Stop after each prompt's gate. Do not create later-phase empty module shells.

| Prompt | Files / focused changes | Validation and dependencies | Estimate |
|---|---|---|---|
| 01 `01-BOOTSTRAP-CONTRACTS.md` | Reviewed root instruction links/reconciliation; `pyproject.toml`, tooling/CI/ignore metadata; `src/judge_lab/{__init__,contracts,load,provenance}.py`; `examples/security_fixture.jsonl` plus manifest/judge spec; `tests/unit/test_contracts.py`, loader/provenance tests, `tests/security/test_judge_view.py`; `worklogs/01-contracts.md`. | Freeze contracts and missing family/exclusion fields first; 8–16 clearly synthetic cases; positive/negative schemas, digest tamper, Unicode, blind input; preserve legacy tests; import/install, pytest/Ruff/mypy. | 2–4 days, medium/high. |
| 02 `02-JUDGE-RUNNER.md` | `src/judge_lab/judges/{base,mock,imported}.py`, runner/artifact writer as needed, strict parser, runner/import/budget tests; `worklogs/02-runner.md`. | Exact case-ID joins, deterministic mock, typed errors, bounds and atomic artifacts; no provider required. | 2–3 days, medium. |
| 03 `03-CALIBRATION-METRICS.md` | `src/judge_lab/metrics/{binary,uncertainty}.py`, metric contracts, `tests/goldens/`, metrics edge tests; `worklogs/03-metrics.md`. | Independent goldens, Wilson, denominator/undefined semantics and slices. | 2–3 days, high statistical care. |
| 04 `04-REPORT-CLI.md` | `src/judge_lab/cli.py`, `reports/{json_report,html_report}.py`, package entrypoint/resources, README/demo instructions, integration/security tests; `worklogs/04-cli.md`. | Offline installed CLI, exact JSON/HTML agreement, redaction/escaping, collisions and safe output paths. | 2–4 days, medium. |
| 05 `05-BASELINE-REPLICATION.md` | `experiments/baseline_200/{PROTOCOL.md,sample.py,import_labels.py,run.py,NOT_RUN.md}` as applicable; family-split/adjudication tests; `worklogs/05-baseline.md`. | Authorized independent source and frozen labels; sampler insufficient-pool guard; mark empirical run unavailable until evidence exists. | 2–4 days tooling; labeling time unknown. |
| 06 `06-CONTROLLED-PROBES.md` | `src/judge_lab/probes/{manifests,validity,evaluate}.py`, controlled fixtures, CLI probe command, negative tests; `worklogs/06-probes.md`. | Valid/invalid synthetic pair; protected truth/rubric; baseline-correct denominator; human review for semantic equivalence. Depends on reviewed baseline protocol. | 3–5 days, high. |
| 07 `07-DIFFERENTIATION-EXPERIMENT.md` | `experiments/DIFFERENTIATION-PROTOCOL.md`, comparison script/report or NOT_RUN record, sourced competitor matrix, budget/holdout tests; `worklogs/07-experiment.md`. | Freeze B0/B1, verify comparability and matched reviewer/model costs, retain negative findings. | 2–4 days tooling; empirical time unknown. |
| 08 `08-RELEASE-GATE.md` | `src/judge_lab/gates/policy.py`, policy schemas/examples, CLI gate, offline CI example, fail-safe tests; `worklogs/08-gate.md`. | Define uncertainty FAIL vs INCONCLUSIVE, provenance checks, non-PASS exit codes, no production deployment. | 2–3 days, high consequence. |
| 09 `09-PILOT-READY.md` | `pilots/{README,INTERVIEW-GUIDE,CONSENT-AND-PERMISSIONS,SUMMARIZE}.md`, five blank records, pilot validation tests; `worklogs/09-pilots.md`. | No invented participants; permission/de-identification and completed-record count. | 1–2 days toolkit; recruitment/completion unknown. |
| 10 `10-INDEPENDENT-REVIEW.md` | `reviews/{INDEPENDENT-REVIEW,GO-NO-GO}.md`, `worklogs/10-review.md`. | Reproduce install/goldens, independent sample/security/statistical review, evidence-based decision; no automatic implementation remediation. | 2–4 days review, reviewer availability unknown. |

## AI Engineer curriculum coverage

Counting rule: compare explicit MVP deliverables with numbered problems 1–38, not every shared concept or the archived expansion. Scope coverage is different from completion. The attached curriculum's done criteria require working code, tests, measured results, trade-offs and the user's ability to explain the work; no such complete problem can be certified from this repository audit.

**One primary problem (#29), five partial overlaps (#13, #14, #16, #20, #21): six relevant numbered problems out of 38. Zero demonstrated complete.** Even #29 is a substantial scoped implementation of its subject, not a promise to satisfy every listed concept or its numerical target.

| Problem | Coverage | What Judge Lab contributes / what remains outside scope |
|---|---|---|
| 29 — Calibrated LLM-as-Judge Eval Framework | Primary | Versioned judge/rubric, independent references, kappa/calibration, comparison, error analysis and CI policy. No promised κ > 0.7; no required labeling UI, few-shot selector, pairwise mode or cost-delta report on every prompt change. Those completion conditions remain unproven or not explicitly required. |
| 13 — Multi-Provider LLM Gateway | Partial | Adapter boundary, parsing, budgets/accounting; existing retry/cache patterns. No async FastAPI gateway, streaming, multi-provider failover, Redis, auth or 100-stream performance target. |
| 14 — Cloud Deployment & CI/CD | Partial | Offline tests and eventual eval CI gate. AWS/Terraform/ECS/HTTPS deployment is excluded. |
| 16 — Observability & Tracing | Partial | Per-result latency/tokens/cost/errors and digest-provenanced runs. No OpenTelemetry/Langfuse tracing, retrieval/tool spans, Grafana or UI-to-trace debugging. |
| 20 — LLM Security Layer | Partial | Scoped prompt-injection probes, independent attack-success measurement, input boundaries and artifact redaction tests. No general deployed protection layer, exfiltration defenses, tool authorization system or broad OWASP coverage. |
| 21 — RAG Evaluation Harness | Partial, transferable evaluation mechanics | Dataset schemas/provenance, experiment runner, judge templates, uncertainty and comparisons. No RAG pipeline, retrieval metrics, faithfulness scorer or nightly scheduler. Shared mechanics do not complete the RAG problem. |
| 38 — Coding-Agent Fluency | Supporting practice only; excluded from six | Agent specs, decomposition, review/worklogs and verification practices help. No shipped capstone feature or published workflow write-up established by this audit; listed tool-specific completion condition not established. |
| 1–12, 15, 17–19, 22–28, 30–37 | Out of scope (31 problems) | No foundations/training, frontend, retrieval product, agent runtime/memory/MCP/trajectory harness, capstones, multimodal, serving or research agent. |

Track T3 (Public Proof) is supported by reproducible experiments and honest write-ups, but is separate from the 38 problems and not completed: three published write-ups and 1–2 OSS PRs are not evidenced. T1/T2 practice is not supplied by this project. Counting development practice (#38) would make seven touched areas, but would overstate implemented product coverage; use six relevant / one primary for planning.

## Scope changes, ADRs and exit gate

See `DECISIONS.md` for instruction placement, package strategy, label/data separation, parser/outcome contract, reproducibility/privacy, statistics, deferred scope and unresolved inconsistencies inside the MVP specs. No ADR has been silently approved.

- Audit deliverables: READY FOR HUMAN REVIEW.
- Implementation/scientific readiness: NEEDS_FIXES / INCONCLUSIVE; unit/lint checks have not run successfully and the new MVP has not been implemented.
- Human review requested: approve the coexistence strategy and exact reuse/rewrite boundaries, decide canonical documentation placement and resolve Phase 01 schema/exclusion ambiguities. Later-stage policy/probe questions can remain explicitly pending until their gates.
- **Next candidate prompt, only after approval:** `JUDGE_LAB_CODEX_MVP_PACK/prompts/01-BOOTSTRAP-CONTRACTS.md`.
- No implementation prompt is currently authorized. STOP after audit.
