# 07 — Experimental design: outdoing 200 labels or admitting we cannot

## Two research questions only
H1: A calibrated judge analysis with targeted error categories and optional case selection delivers verified incremental value beyond conventional evaluation of a frozen 200-case labeled set.
H2: Independently validated, limited adversarial probes discover previously unseen failure types on held-out cases, net of added model calls, reviewer effort, and error costs.

## Baseline B0 (must actually implement)
Customer's judge, fixed rubric, same adapter settings + **200 hand-labeled, representative and independently reviewed examples** with conventional confusion matrix and per-class errors. Construct a documented source and sampling protocol. If real labels are unavailable, code and test using synthetic data, but mark actual B0 empirical testing **NOT PERFORMED**.

## Candidate B1
Same model/version/rubric, same baseline 200 labeled examples; additional Judge Lab sampling/probe method and review workflow, with a **predeclared matched resource budget**. Compare against B0+an equally budgeted naive alternative (random sampling or fixed attack strings) rather than B0 alone if B1 uses more tokens/reviewer time.

## Unit of generalization
A security incident *family*, not a duplicated report variant. Split by incident family or source scenario. Maintain development, calibration and sealed holdout splits. No leak from model tuning or test case development into held-out measurement. If dataset distribution differs from production, disclose limitation.

## Data protocol
- Get explicit rights to use each source. Prefer synthetic seeded incidents and public, licensed corpora; human-review important semantic cases.
- Preserve immutable labels/reasons/annotator protocol and adjudication history, with annotators blind to tested judge outputs if possible.
- Track label disagreement, case severity, source, incident family and data inclusion/exclusion rules.
- Pre-register H1/H2, success metrics, stop criteria, thresholds and analysis plan before inspecting held-out results.
- Use enough independently sampled cases to support desired uncertainty bounds; 200 overall cases may be insufficient for rare serious defect classes. Do not invent power claims.

## Evaluation outcomes
Primary: additional **unique verified material false-accept failures** discovered per 100 cases and per reviewer-hour at matched spend, with holdout provenance. Secondary: false accept rate, error-type coverage, sensitivity to judge version drift, time to reproduce, review minutes, false alarms/invalid probes, dollar cost, legitimate-case coverage.

## Fairness checks
- Compare same judge/model settings and baseline evidence for overlapping measurements.
- Treat repeated probe attempts as correlated; don't inflate n by counting variants as independent.
- Show paired outcomes when judges or treatments view identical incidents; preserve order randomization.
- State if any baseline uses fewer model calls, fewer labels or less human effort.
- Separate train/development improvement from held-out generalization.

## Minimal analysis table (fill after real experiment)
| Measure | B0 200-label baseline | B1 Judge Lab | Increment | Evidence status |
|---|---|---|---|---|
| Unique confirmed false accepts | NOT RUN | NOT RUN | N/A | Awaiting data |
| Reviewer minutes | NOT RUN | NOT RUN | N/A | Awaiting measurement |
| Model/API spend | NOT RUN | NOT RUN | N/A | Awaiting measurement |
| Invalid probe fraction | N/A | NOT RUN | N/A | Awaiting measurement |
| False-positive review burden | NOT RUN | NOT RUN | N/A | Awaiting measurement |

## Falsification / kill conditions
If Judge Lab adds no reliably verified value at matched budget, don't claim superiority. Evaluate whether (a) simpler reporting/CI integration has real utility, (b) narrow workflows merit productization, or (c) stop. A "failed" hypothesis is still meaningful research when accurately reported.
