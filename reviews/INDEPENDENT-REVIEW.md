# Phase 10 review — external independent approval pending

Date: 2026-10-17 UTC. Scope: current `judge_lab` package, preserved legacy tests,
canonical specs 01–11, decisions, fixtures, reports and worklogs. This is an
implementation-agent **self-review**, not an independent person/team's sign-off.
The filename follows the phase prompt; it does not establish reviewer independence.
An independent numerical sample audit used sklearn and SciPy implementations,
separate from Judge Lab's formulas. No model/provider or production target used.

## Executed evidence

| Check | Actual outcome |
|---|---|
| `.venv/bin/python -m pytest -q` | 260 passed, 1 live test deselected, 26.84 s, exit 0; 190 new + 70 legacy tests |
| `make lint` | Ruff passed, exit 0 |
| `make typecheck` | 18 package source files passed, exit 0 (includes final packaged fixture module) |
| Independent numeric sample audit | 255 nonempty small 2x2 confusion tables compared with sklearn; Wilson endpoints compared with SciPy across n=1,2,20,50,200,10000, tolerance 1e-12; 2 tests passed |
| Wheel build and new venv install | Successful without provider/network access, cached dependency wheels; resources explicitly packaged |
| Installed CLI from `/private/tmp` | Demo twice, validate, frozen import twice, probe all exit 0; synthetic gate exit 4 |
| Reproducibility | Frozen imported reports byte-identical; demos have equal run compatibility ID/observations/statistics (timestamps differ by design) |
| Probe demonstration | 1 valid, baseline-correct, planted-rule false accept in vulnerable mock; 2 calls, one development family, no holdout claim |
| Comparison / pilots | NOT_PERFORMED exit 4 / NO_REAL_PILOT_DATA exit 0, respectively |

Build/check records are local under `runs/final-verification/`, deliberately ignored.
Remote GitHub CI/Python 3.12 execution is NOT VERIFIED. Actual local interpreter:
CPython 3.14.8, macOS arm64. A successful test suite is not proof of no defects:
the additional concurrency reproduction below exposes an untested failure.

## P0 blockers

No P0 defect reproduced in the local offline scope. This is not an exhaustive
security audit and does not establish safety for hostile multi-user environments.

## P1 substantive findings

### P1-01: output installation can overwrite an unrelated concurrent directory

Evidence: `src/judge_lab/artifacts.py:21` validates existence/ownership once;
`:37` checks existence again but does not repeat the overwrite/ownership condition.
`:40` moves whatever now exists; `:49` deletes its backup after installation.
A second writer can therefore create a non-owned target between validation and
installation, and that directory is deleted even with overwrite=False. Ancestor
symlink checks also occur before later filesystem operations; shared writable
parents are outside the protected boundary.

Reproduce safely: `.venv/bin/python reviews/reproduce_output_race.py`.
Actual output: `{"new_report_installed": true, "unrelated_file_preserved": false}`,
exit 0. The script injects a second writer only inside a disposable temporary
directory and deletes no real user data. It is a defect reproduction, not a passing
security assertion. Normal pre-existing collision/symlink tests still pass.

Disposition: NEEDS_FIXES before sharing output directories, running parallel jobs
against a common output, or claiming race-safe overwrite protection. For now use a
private directory and unique output per process. The Phase 10 prompt says “do not
auto-fix high-risk defects in the review task”; no concurrency rewrite was made.
A follow-up must add failing race/rollback tests and reserve ownership atomically,
including explicit behavior for stale reservations and unsupported filesystems.

### P1-02: independent scientific/customer approval is absent

Evidence: `experiments/NOT_RUN.json`, `experiments/baseline_200/NOT_RUN.md`, all five
`pilots/templates/P*.json` records and `worklogs/09-pilots.md`. Actual independently
adjudicated baseline supplied: none. Empirical H1/H2 measurements: none. Completed
real pilots: zero. Independent external reviewer: none. Authorization to implement
does not supply these observations. Stage C acceptance and claims of empirical
superiority/customer validation remain blocked on actual evidence.

### P1-03: novel transformed-population H2 comparison is not implemented

Evidence: `src/judge_lab/experiments.py:127` explicitly requires identical frozen
observations. This correctly supports equal-resource review-workflow comparison,
but cannot compare baseline fixed attacks with distinct targeted probe populations.
Phase 06 validates one narrow synthetic planted defect only. The differentiation
protocol documents the limitation; the full H2 experiment needs a reviewed mapping
of original/variant families, independent validity records and measured costs.
Do not present this partial scope as a completed empirical adversarial study.

## P2 improvements / bounded trust assumptions

- **Attestations are not authenticated evidence.** `gates.py:43` accepts supplied
  probe/approval record hashes; `:92` binds them to policy/report but does not open
  or verify signatures on those external records. Baseline adjudicators and pilot
  participants are similarly declarations. Gate PASS is only defensible with a
  trusted custodian verifying source records and expected digests, as documented
  in docs/gates.md. It cannot serve as unattended production release authority.
- **Report slices are not independently recomputed on import.** `reports.py:95`
  verifies the overall hash/run, unique observations and aggregate statistics,
  but not `slice_breakdowns`. Replacing a slice count and recomputing report_digest
  was accepted by verify_report with aggregate statistics unchanged. Gates use
  recomputed aggregates, so this does not directly bypass their threshold checks.
  A trusted expected report digest rejects the alteration. Future schema should
  bind slice membership and permit deterministic slice recomputation.
- **Severity and probe evidence live in separate artifacts.** General calibration
  has family/defect slices, but no severity field. Probe summaries and gate critical
  attestations are separate files, not a single integrated report. Link/bundle them
  with a reviewed evidence manifest before a user expects one complete audit pack.
- **Single-family probe uncertainty is limited.** Success denominator is valid +
  baseline-correct, including attacked abstains/errors as non-success. One fixture
  has no generalization claim. Formatting gets REVIEW_REQUIRED, not semantic proof.
- **Resource and preregistration declarations need measurement.** Exact equal
  ledgers and family disjointness are checked; the tool cannot prove wall-clock
  review minutes, distinct humans, pre-outcome plan timing or representative source
  sampling. Targeted findings do not receive independent-random-sample CIs.
- **Platform coverage.** Fresh wheel works locally; Python 3.12/Linux remote CI and
  Windows filesystem/process semantics have not been executed by this session.

## Positive boundaries actually exercised

Strict label/JSON/YAML parsing; unknown schemas; duplicate IDs; reference/split
isolation; digest mismatch; timeout/cancellation/call caps; explicit parse errors;
missing labels; zero denominators; undefined kappa; family dependence; HTML escaping;
source canary omission; traversal, symlinks and existing ownership checks; protected
probe mutations; same-family split protection; unequal comparison resources;
missing holdout/classes/probes/approval; policy changes; duplicate/synthetic pilots.
No arbitrary strings execute as tools/shell, and new CLI has no provider adapter.
Legacy provider/retry/cache behavior remains separate and is not security-hardened
by this project. Existing legacy risks from the audit still apply to that workflow.

## Review conclusion

Useful local engineering/toolkit evidence exists. Shared-output safety needs a fix;
H2 comparison and independent empirical/customer validation remain incomplete.
Do not claim production-ready gates, external independent approval, general safety,
measured commercial superiority or five validated users. See GO-NO-GO.md and the
single proposed follow-up in REMEDIATION-PROMPT.md.
