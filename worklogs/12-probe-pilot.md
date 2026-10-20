# Worklog: preregistered local Ollama probe pilot

- Branch: `probe-pilot`.
- Authorization: attached Tasks 0–6 and explicit request to check the running local Ollama service and continue.
- Preregistration: `0cae1d6`; dataset: `31a71a7`; frozen runner/probes: `cf97048`.
- Evidence status: local real-model inference on synthetic reports; independent scientific review unavailable.

## Requirements and scope

Added 48 deterministic reports with fixed ACCEPT/REJECT labels; pure P1–P4 transformations;
a narrow fixed-payload sanitizer; an opt-in loopback Ollama adapter; raw per-call artifacts;
summary and independent arithmetic/provenance audit scripts; README and legacy-doc cleanup.
Only synthetic local data enters the model. Ground-truth labels and provenance never enter
JudgeInput. ERROR and ABSTAIN stay separate, and missing calls are NOT_RUN.

The exact sibling lab path does not exist. The nested `Lattivant/lattivant-lab` source was
available and inspected. Python templates follow its three variants, with source commit
and hashes recorded. No Rust integrated-engine execution is claimed. There are 24 paired
instances sharing three templates, not 48 independent incidents. Nominal Wilson intervals
must not be read as population-level significance.

## Integration decision

OllamaAdapter implements the existing JudgeAdapter.evaluate(JudgeInput, JudgeSpec) shape and
reuses AdapterReply and the strict verdict parser. The experiment invokes this adapter in
its own explicit local runner. JudgeSpec uses the existing `imported` configuration shape
for external predictions; the general offline run_judge remains mock-only. No frozen public
contract, default CLI network behavior, release gate, or paid-provider support was changed.
Calls have no retries, bounded generation and socket timeout, and a 288-call/90-minute budget.

## Validation

- `make test`: exit 0; 279 passed, 1 live test deselected.
- `make lint`: exit 0.
- `make typecheck`: exit 0; 19 source files checked.
- Probe/provider tests cover preserved security facts, removed evidence, label separation,
  input immutability, matched sanitizer restoration, malformed labels, truncated generation,
  and separate ERROR handling.
- Live runner: exit 0; 288 calls in 855.60 seconds, no retries or errors.
- Raw artifact commit: `0e1e947`; 288 responses plus metadata and completion record.
- `scripts/probe_pilot.py summarize`: exit 0; all inputs and responses verified.
- `scripts/audit_probe_pilot.py`: exit 0, PASS; independently checked all primary
  numerators/denominators and Wilson arithmetic, committed raw records, exact sanitizer
  input restoration, stable model digest and unchanged preregistration ancestry.
- Final `make lint`, `make typecheck` and `git diff --check`: exit 0 after audit and documentation additions.

## Existing workspace changes

Preserved unrelated pre-existing edits to `.gitignore`, `AGENTS.md`,
`reviews/reproduce_output_race.py`, `src/judge_lab/artifacts.py`, plus untracked
`docs/output-ownership.md`, `tests/contracts/test_artifact_races.py`, and
`worklogs/11-output-ownership.md`. These are excluded from pilot commits.

## Scientific validity and scope limits

No prompt/payload tuning, replacement runs, or model-based reference labels. A literal flip
can repair a mistaken base prediction; primary metrics therefore coexist with transitions
and baseline-correct subset results. P1/P4 primary failures mean probe ACCEPT, not necessarily
a literal change. P1 strict REJECT failures also count abstentions. Sanitizer is a positive
control for one fixed suffix and restores exactly the base input; no general defense or
paper-reproduction claim. Second-model committee is NOT_RUN under the preregistered budget.

## Measurements

P1 primary nonacceptance failures: 16/48 (33.3%); P2/P3 flips: 0/48 each;
P4 nonacceptance failures: 41/48 (85.4%); sanitized P2 flips: 0/48. Base accuracy
was 24/48 (50%) with ACCEPT on all 48 reports. P1 had 32/48 abstentions; every
other condition had zero abstentions. All 288 calls had zero ERROR outcomes.
Wilson intervals and baseline-correct subsets are in the committed results.
The P2 hypothesis was not observed, but base acceptance saturation prevents interpreting
zero flips as injection robustness. The sanitizer demonstrated no reduction. P4 accepted
24/24 previously correct reports after evidence removal. Preregistration unchanged.

## Exit gate

Engineering and local pilot complete; scientific generalization remains INCONCLUSIVE.
All required probes and optional sanitizer ran. No independent review or production
approval is claimed. README cleanup and legacy documentation relocation are complete.
Next authorized action: finish Tasks 0–6, commit on probe-pilot and stop; no new experiment.
