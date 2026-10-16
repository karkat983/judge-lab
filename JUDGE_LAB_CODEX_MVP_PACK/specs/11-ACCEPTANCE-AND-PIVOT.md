# 11 — Acceptance rubric and pivot criteria

## Stage A acceptance
- A stranger can install repo from clean environment, run `judge-lab calibrate` with bundled **synthetic** demo and get matching JSON/HTML report.
- Input contracts reject missing/invalid labels and duplicate IDs; imported predictions join only by case ID, not order.
- Golden confusion, kappa, abstain/error, Wilson calculations pass, including undefined edge cases.
- Tests prove references aren't passed to judge prompt; source+license and digests recorded.
- Run's empirical claim clearly distinguishes synthetic test from external validation.
- Baseline `200 labels` protocol established without fabricating annotations; actual empirical baseline tested only when labels exist.

## Stage B acceptance
- At least one controlled probe yields a valid attempted transformation and case outcome in a synthetic regression test. A deliberately invalid probe is rejected.
- Correctness of attack success denominator is independently tested; abstains/errors not secretly wins.
- Heldout/case-family split and cost matching are enforced, not just recommended.
- Baseline-vs-Judge-Lab comparison script produces results from actual inputs and states `NOT PERFORMED` if no data.
- Gate tests demonstrate fail-safe uncertainty, integrity and safety behavior.

## Stage C acceptance
- Real human approval and data permission flow exist; pilot records are deidentified and reproducible.
- Five **completed real-user** pilots are documented before saying "validated by five users". Zero pilots = zero user validation, even with a polished template.
- Independent statistical/security reviewer notes unresolved weaknesses and misleading claims.
- An evidence-led decision memo selects ship/integrate/pivot/stop.

## Quality criteria for every change
1. Does it improve correctness or value relative to simplest baseline?
2. Is it falsifiable and reproducible?
3. Does it preserve independent ground truth and frozen holdout?
4. Can it leak user data or amplify model-generated authority?
5. Is there a unit/integration/negative test for the core claim?
6. Is the user-facing terminology narrowly scoped and honest?
7. If uncertain, would a reviewer prefer INCONCLUSIVE rather than an unsupported green light?

## Definition of "done"
Done means implemented + tests run + working demo + stable data contract + documented limitations + review worklog. Code that merely compiles or an architecture diagram does not satisfy done. Do not continue until a human reviews major gate results.
