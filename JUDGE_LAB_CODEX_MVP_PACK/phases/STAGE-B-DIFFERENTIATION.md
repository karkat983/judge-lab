# Stage B — Extra validated failures at matched budget

**Execute prompts 06–08 sequentially.** Goal: demonstrate real *incremental* value beyond conventional evaluation or know that we haven't.

## Controls
- Locked rubric, frozen human reference and case-family split.
- Fixed, bounded attack set and clear lower-trust field; no autonomous attacker.
- Independent structural or human oracle; candidate judge cannot certify its own attack.
- Cost-matched baseline with equally available model calls and reviewer time.
- Holdout measured once according to pre-registered protocol; do not tune on observed failures then re-present on same test set.

## Deliverables
Probe run manifest, validity decisions, clean and attacked predictions, conditional attack success with counts, baseline-vs-B1 comparison, regression corpus, conservative policy with documented exit-code semantics, objective report with limitations.

## Failure is a valid outcome
If a fixed attack tests no useful failures, show that. If B1 needs more review cost to find the same errors, report that. If everything is synthetic, state the limitation. Never turn a dashboard success into a claim of research novelty.

## Human gate
Approve Stage C only if usable local workflow exists and enough evidence suggests prospective users would find the comparison worth trying. If not, pivot (better integration or evaluator error discovery focus) or stop.
