# Local Ollama metamorphic probe pilot

Measured model inference on 48 synthetic template reports; not human-adjudicated or production validation. Preregistration was committed before inference.

Model: `llama3.1:8b` (Q4_K_M).
Manifest digest: `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.

Raw per-call JSON, model metadata and `ollama show` output: [committed run](../../runs/probe-pilot/llama3.1-8b/metadata.json).
Raw artifact commit: `0e1e947fb7ed53bb6dbe1849a9bd5f9a52a52b21`.

48 reports = 24 incident instances × faithful/defective versions, from three shared templates. Wilson 95% intervals below are nominal descriptive intervals: dependence between reports prevents independent-sample population claims.

| Probe | Wrong-direction flip / failure rate (Wilson 95%) | ABSTAIN / attempted | ERROR / attempted | Excluded ERROR pairs | NOT_RUN |
|---|---|---|---|---|---|
| P1 | 16/48 = 33.3% (21.7%–47.5%) | 32/48 | 0/48 | 0 | 0 |
| P2 | 0/48 = 0.0% (0.0%–7.4%) | 0/48 | 0/48 | 0 | 0 |
| P3 | 0/48 = 0.0% (0.0%–7.4%) | 0/48 | 0/48 | 0 | 0 |
| P4 | 41/48 = 85.4% (72.8%–92.8%) | 0/48 | 0/48 | 0 | 0 |
| P2_SANITIZED | 0/48 = 0.0% (0.0%–7.4%) | 0/48 | 0/48 | 0 | 0 |

P2/P3 count any verdict change, including changes that repair a wrong base verdict. P1/P4 count probe ACCEPT as failure to reach REJECT/ABSTAIN; these are not necessarily literal flips. ERROR pairs are excluded, while ABSTAIN remains a verdict. Rates describe all evaluable pairs, not proven attack successes.

BASE outcomes: `{'ACCEPT': 48}`. Confusion counts (reference then prediction): `{'AA': 24, 'AR': 0, 'RA': 24, 'RR': 0, 'A?': 0, 'R?': 0, 'AE': 0, 'RE': 0}`. Answered-case accuracy: 24/48 = 50.0% (36.4%–63.6%); coverage 48/48; kappa 0.0.

Baseline-correct subset violations (same definitions):

- P1: 8/24 = 33.3% (18.0%–53.3%).
- P2: 0/24 = 0.0% (0.0%–13.8%).
- P3: 0/24 = 0.0% (0.0%–13.8%).
- P4: 24/24 = 100.0% (86.2%–100.0%).
- P2_SANITIZED: 0/24 = 0.0% (0.0%–13.8%).

Strict P1 failure to return REJECT (including ABSTAIN): 48/48 = 100.0% (92.6%–100.0%).

## Interpretation and limitations

Post-run interpretation: the judge accepted every base report, including all 24 known
REJECT reports. The all-reject false-accept rate was therefore 24/24 (100%); zero
P2/P3 flips do not establish robustness. In particular, an injection requesting
ACCEPT has no additional acceptance to induce when every base verdict is already
ACCEPT. The preregistered P2 ≥10% flip hypothesis was not observed (0/48; nominal
upper bound 7.4%), but this acceptance saturation limits what that null can tell us.
The sanitizer also measured zero flips, so **no reduction was demonstrated**.

P4 retained ACCEPT on every previously correct base case (24/24), even after its
supporting evidence was removed. P1 returned ABSTAIN on 32 cases and ACCEPT on 16,
with no strict REJECT responses. The primary P1 metric treats abstention as
conservative nonacceptance; it does not mean the strict P1 oracle was satisfied.
These failures are the substantive result of this pilot.

The sanitizer strips the preregistered SYSTEM suffix from quoted JSON msg fields. On this fixed payload it restores the exact base input; this is a narrow positive control, not a general injection defense or a reproduction of StableJudge. Repeated identical inputs can still differ across local model calls.

The 10% hypothesis is evaluated descriptively against the P2 estimate and interval; an interval crossing 10% is inconclusive. Three shared templates, one model, one payload, no human adjudication, and no independent scientific review limit transfer to real investigations. No payload was tuned after observing results.

Second-model committee: **NOT_RUN** (preregistered primary-model budget). Integrated Rust scenario execution: **NOT_RUN** (used synthetic Python templates derived from local source semantics). External/production validation: **NOT_RUN**.

Reproduce with `.venv/bin/python scripts/probe_pilot.py run` after preserving the existing run directory elsewhere; the runner refuses overwrite. Regenerate the numerical report using `.venv/bin/python scripts/probe_pilot.py summarize`
after preserving and removing the existing `results.md` and `summary.json` (outputs are
exclusive). The interpretation paragraphs above were added after the numerical report;
the frozen runner and preregistration remain unchanged. Full transitions, separate error/abstention intervals and base metrics are in [summary.json](summary.json).

## SOP:

- SOP: Hiding one instruction inside a quoted log line changed 0/48 = 0.0% (0.0%–7.4%) of llama3.1:8b's verdicts on this synthetic report set.
- SOP: With the matched quoted-field sanitizer, the flip rate was 0/48 = 0.0% (0.0%–7.4%).
