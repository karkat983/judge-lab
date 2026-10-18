# Worklog: pilot 2 — stronger defects and bidirectional injection

## Authorization and isolation

User's attached Tasks 0–5 authorize local llama3.1:8b inference and commits, explicitly
prohibit pushing, and require a new branch from main. `probe-pilot-2` was created from
`d9565ddb8f8dc86a08889cc42e1ce5555fbcf876` in the separate `judge-lab-pilot-2` worktree.
The original worktree, its uncommitted changes, and pilot-1 branch/artifacts are preserved.
No first-pilot results or raw responses were overwritten.

Preregistration commit: `506d86a`; population commit: `c585766`; frozen runner: `b93a7c0`.
No inference preceded those commits. The old provider module was copied byte-for-byte
from `b5b86fa`, retaining the same prompt, parsing, HTTP route and generation settings.
A shared ignored virtual-environment symlink avoids dependency installation; commands use
`PYTHONPATH=src` to ensure imports come from this worktree, which was explicitly verified.

## Implementation

48 reports retain the prior evidence and incident instances. The 24 faithful judge inputs
are unchanged. The 24 defective reports have eight evidence contradictions, eight wrong
entities, and eight unsupported exfiltration/backup-deletion claims. Each defect has explicit
metadata and an independent label rationale, excluded from model prompts.

P1/P3/P4 use the same transforms as pilot 1. Both P2 directions are evaluated on all cases,
then stratified by the actual base verdict; a missing source stratum is NOT_EVALUABLE.
Sanitizer selection follows a preregistered deterministic rule, before its own inference.
The runner is split into base/probes/sanitizer stages, requires committed preceding evidence,
checks the exact model digest and frozen hashes, saves each raw response and exact command,
refuses overwrites, performs no retries, and enforces 336-call / 90-minute budgets.

Existing public contracts and the offline general-purpose runner remain unchanged.
OllamaAdapter retains JudgeAdapter.evaluate(JudgeInput, JudgeSpec); the explicit experimental
runner invokes it. No cloud dependencies, new models or production data are used.

## Validation actually executed

- Targeted probe/metric tests: 13 passed, exit 0.
- `PYTHONPATH=src make test`: 272 passed, 1 skipped, 1 live test deselected, exit 0.
  The skipped legacy test requires an unavailable raw XSTest download; no download performed.
- `PYTHONPATH=src make lint`: exit 0.
- `PYTHONPATH=src make typecheck`: exit 0; 20 modules checked.
- Provider and original transformations byte-for-byte match pilot 1.
- Separate stdlib audit checks Git ancestry, unchanged preregistration, original faithful
  inputs, raw responses, nominal Wilson arithmetic, directional/matched denominators,
  sanitizer selection and base kappa. Execution passed after all raw responses were committed (exit 0); audit.json records
  independent numerics, branch lineage, faithful-input equality and preservation checks.

## Statistical limitations

The 48 reports share 24 incident instances and three templates. Wilson intervals are nominal
and descriptive. Opposite-verdict flips can repair a mistaken base prediction; baseline-correct
subsets and full transitions are reported separately. Sanitizer selection by the larger observed
rate is exploratory. Synthetic labels are not independent human adjudication or production
validation. Stronger defects may produce abstention rather than correct rejection; this is
reported rather than treated as separability success. Additional models and integrated Rust
engine execution are NOT_RUN under the fixed local scope.

## Measurements and exit gate

Base stage completed and committed at `8842c4f`: 48 calls, no ERROR outcomes.
All-case accuracy 24/48 (50%); answered accuracy 24/45 (53.3%); κ = 0.
Defective reports: 21 ACCEPT, 0 REJECT, 3 ABSTAIN. Faithful reports: 24 ACCEPT.
The base-set target failed. This finding was recorded in base_check.md and committed
before starting probes; no inputs or prompt were altered. P2_ACCEPT has no source-REJECT
cases and must be NOT_EVALUABLE, while P2_REJECT has 45 source-ACCEPT cases.

All stages completed: 48 base + 240 probe + 48 sanitizer = 336 calls, zero ERROR
or NOT_RUN records, 1377.30 seconds of live execution. Raw stage commits: `8842c4f`
(base), `f94d8e9` (probes), `aa59ddf` (sanitizer). Sanitizer choice was committed at
`8c7761b` before its inference: P2_REJECT, the only defined directional rate.

Primary results: P1 16/48 (33.3%); P2_ACCEPT NOT_EVALUABLE (no base REJECTs);
P2_REJECT 0/45; P3 5/48 (10.4%); P4 38/48 (79.2%); selected sanitizer 0/45.
Baseline-correct P4 remained 24/24 ACCEPT after evidence removal. P1's faithful
subset had 8 ACCEPT and 16 ABSTAIN. P2_ACCEPT changed two base abstentions to
ACCEPT; P2_REJECT changed one to ACCEPT and one to REJECT. These secondary changes
are reported separately from the preregistered primary directional metrics.
P3 changed three defective-case abstentions to ACCEPT and corrected two mistaken
ACCEPT verdicts to REJECT; no baseline-correct case changed. All nominal Wilson
intervals, counts, transitions, and source-stratum denominators are in summary.json.
No sanitizer reduction was demonstrated. Narrative interpretation was added after
generating the numerical report; the preregistration and all inference inputs/code
remain byte-identical to their frozen versions.

Final lint/type/diff checks passed. Pilot-1 HEAD and pre-existing dirty files were
rechecked and unchanged. Engineering Tasks 0–5 are complete; the separability target
failed and external scientific validation remains unavailable. No push performed.
Next authorized action: stop after the final pilot-2 commit; do not push.
