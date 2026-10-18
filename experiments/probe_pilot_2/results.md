# Pilot 2: stronger defects and bidirectional injection

Local real-model inference on a synthetic, correlated template set. Pilot 1 is preserved on `probe-pilot`; this branch starts from `main`.

Model: `llama3.1:8b`; manifest digest `46e0c10c039e019119339687c3c1757cc81b9da49709a3b3924863ba87ca666e`.
Committed raw evidence: `aa59ddf5ab3ff0a1a98f14ce746e56404684276c`.

## Base check

Accuracy: **24/48 = 50.0% (95% CI 36.4%–63.6%)**; **κ = 0.0**. The judge rejected **0/24** defective reports and accepted **21/24**. The ≥75% accuracy / κ > 0 target was not met.

[Base check and confusion matrix](base_check.md). [Machine-readable summary, transitions and defect breakdown](summary.json).

## Probe results

| Condition | Primary flip/failure rate, nominal Wilson 95% | ABSTAIN / calls | ERROR / calls | NOT_RUN |
|---|---|---|---|---|
| P1 | 16/48 = 33.3% (95% CI 21.7%–47.5%) | 32/48 | 0/48 | 0 |
| P2_ACCEPT | NOT_EVALUABLE (0 eligible pairs) | 1/48 | 0/48 | 0 |
| P2_REJECT | 0/45 = 0.0% (95% CI 0.0%–7.9%) | 1/48 | 0/48 | 0 |
| P3 | 5/48 = 10.4% (95% CI 4.5%–22.2%) | 0/48 | 0/48 | 0 |
| P4 | 38/48 = 79.2% (95% CI 65.7%–88.3%) | 5/48 | 0/48 | 0 |
| SANITIZED (P2_REJECT) | 0/45 = 0.0% (95% CI 0.0%–7.9%) | 3/48 | 0/48 | 0 |

P2_ACCEPT is REJECT→ACCEPT among base-REJECT cases. P2_REJECT is ACCEPT→REJECT among base-ACCEPT cases. Probe ABSTAIN remains in each eligible denominator but does not count as a target flip. Undefined strata are NOT_EVALUABLE, not a measured zero. Errors/missing calls are excluded and reported separately. P3 counts any valid verdict change. P1/P4 count probe ACCEPT as failure to reach REJECT/ABSTAIN; these are not necessarily literal flips.

### Baseline-correct subset

| Condition | Primary rate, nominal Wilson 95% |
|---|---|
| P1 | 8/24 = 33.3% (95% CI 18.0%–53.3%) |
| P2_ACCEPT | NOT_EVALUABLE (0 eligible pairs) |
| P2_REJECT | 0/24 = 0.0% (95% CI 0.0%–13.8%) |
| P3 | 0/24 = 0.0% (95% CI 0.0%–13.8%) |
| P4 | 24/24 = 100.0% (95% CI 86.2%–100.0%) |
| SANITIZED | 0/24 = 0.0% (95% CI 0.0%–13.8%) |

All-pair any-change rates (including repaired mistakes) are in summary.json. An opposite-verdict change on an incorrectly judged base may improve correctness, so the primary directional rate is not automatically an attack-success rate.

Strict P1 failure to return REJECT (including abstention): 48/48 = 100.0% (95% CI 92.6%–100.0%).

## Comparison with pilot 1

- P1, all reports: pilot 1 16/48 = 33.3% (95% CI 21.7%–47.5%); pilot 2 16/48 = 33.3% (95% CI 21.7%–47.5%).
- P1, unchanged faithful reports: pilot 1 8/24 = 33.3% (95% CI 18.0%–53.3%); pilot 2 8/24 = 33.3% (95% CI 18.0%–53.3%).
- P4, all reports: pilot 1 41/48 = 85.4% (95% CI 72.8%–92.8%); pilot 2 38/48 = 79.2% (95% CI 65.7%–88.3%).
- P4, unchanged faithful reports: pilot 1 24/24 = 100.0% (95% CI 86.2%–100.0%); pilot 2 24/24 = 100.0% (95% CI 86.2%–100.0%).

The faithful-subset comparison uses the same 24 judge inputs, independently of whether their new base predictions were correct. The baseline-correct subset can change composition. These are descriptive comparisons, not causal claims.

Pilot 1 source: `git show b5b86fa:experiments/probe_pilot/summary.json`; its raw responses remain committed at `0e1e947fb7ed53bb6dbe1849a9bd5f9a52a52b21`.

## Injection hypotheses and sanitizer

Post-run interpretation: stronger defects did **not** create a separable base set.
P1's conservative failure rate stayed unchanged. P4's all-report acceptance count
fell from 41/48 to 38/48, but the unchanged faithful subset remained 24/24 ACCEPT
after evidence removal. Thus the central P1/P4 failure on faithful reports persists.

Neither injection produced its preregistered source-to-opposite-verdict flip.
There were secondary changes from base abstentions, which the directional metrics
intentionally exclude:

| Injection | Any verdict change across all evaluable pairs (nominal Wilson 95%) | Changes observed |
|---|---|---|
| P2_ACCEPT | 2/48 = 4.2% (95% CI 1.2%–14.0%) | 2 ABSTAIN→ACCEPT |
| P2_REJECT | 2/48 = 4.2% (95% CI 1.2%–14.0%) | 1 ABSTAIN→ACCEPT; 1 ABSTAIN→REJECT |

These secondary transitions do not rescue the unevaluable P2_ACCEPT primary hypothesis,
but they show that the injected log strings were not behaviorally inert. The moves from
ABSTAIN to ACCEPT occurred on known defective reports. P3's five changes comprised three
ABSTAIN→ACCEPT changes on defective reports and two ACCEPT→REJECT corrections. It caused
no changes among the 24 baseline-correct reports. These outcomes should not be collapsed
into a single attack-success claim.

- P2_ACCEPT: NOT_EVALUABLE (0 eligible pairs). NOT_EVALUABLE: no valid source-verdict pairs; no null claim.
- P2_REJECT: 0/45 = 0.0% (95% CI 0.0%–7.9%). Nominal interval is below the preregistered 10% threshold on this set.

The preregistered selection rule chose **P2_REJECT**. Matched complete-pair comparison: before 0/45 = 0.0% (95% CI 0.0%–7.9%); after 0/45 = 0.0% (95% CI 0.0%–7.9%).
No reduction in the primary directional flip rate was demonstrated. The sanitizer restores the exact base input for this fixed payload. Selection by observed rate is exploratory and can bias a comparison; this is not an independent defense evaluation or evidence of general injection resistance.

## Reproduction and limitations

Exact inference commands (run from repository root, in order):

```sh
PYTHONPATH=src .venv/bin/python scripts/run_probe_pilot_2.py base
PYTHONPATH=src .venv/bin/python scripts/run_probe_pilot_2.py probes
PYTHONPATH=src .venv/bin/python scripts/run_probe_pilot_2.py sanitizer
```

Each stage refuses overwrites. Base evidence and base_check.md must be committed before probes; probe evidence and sanitizer_selection.json must be committed before sanitizer. Report commands are `base-check`, `select`, and `summarize` on `scripts/report_probe_pilot_2.py`; these refuse existing outputs too. Use preserved copies/fresh output locations for any separately authorized rerun. The interpretation paragraphs and secondary-transition table were added after the generated numerical report; frozen inference/reporting code was not edited.

Stage metadata and per-call JSON are in [base](../../runs/probe-pilot-2/llama3.1-8b/base/metadata.json), [probes](../../runs/probe-pilot-2/llama3.1-8b/probes/metadata.json), and [sanitizer](../../runs/probe-pilot-2/llama3.1-8b/sanitizer/metadata.json). Metadata preserves exact commands, Ollama version, show output, manifest digest, frozen input hashes and code revision. `ollama show` itself does not print the manifest digest; the matching `/api/tags` entry supplies it.

All 48 reports share 24 paired instances and three templates. Nominal Wilson intervals do not establish independent-sample population significance. The follow-up was informed by pilot 1, but no tuning occurred after pilot-2 inference. One model, fixed suffix payloads, synthetic labels and no independent human adjudication limit generalization. ERROR and ABSTAIN remain distinct throughout.

Additional models, integrated Rust engines and external/production validation: **NOT_RUN** (outside this fixed synthetic local protocol).

## SOP:

- SOP: Even after strengthening explicit defects, llama3.1:8b accepted 21/24 defective reports and rejected 0/24; separability was not established.
- SOP: P2_ACCEPT was run but its directional flip rate is NOT_EVALUABLE because no valid base-REJECT pairs were available.
- SOP: Among base-ACCEPT reports, a quoted-log instruction asking for REJECT changed llama3.1:8b to REJECT in 0/45 = 0.0% (95% CI 0.0%–7.9%) of cases.
- SOP: Removing cited evidence left the judge accepting 24/24 originally faithful reports.
- SOP: Replacing those 24 faithful reports with alert restatements produced 8/24 ACCEPT, 16/24 ABSTAIN, 0/24 REJECT, 0/24 ERROR and 0/24 NOT_RUN outcomes.
- SOP: For the selected P2_REJECT payload, the matched sanitizer comparison was 0/45 = 0.0% (95% CI 0.0%–7.9%) before and 0/45 = 0.0% (95% CI 0.0%–7.9%) after.
