# 04 — Metrics, statistical conventions, and numerical goldens

## Confusion matrix (reference rows, judge columns)

| Reference \\ Prediction | ACCEPT | REJECT | ABSTAIN | ERROR |
|---|---:|---:|---:|---:|
| ACCEPT | AA | AR | A? | AE |
| REJECT | RA | RR | R? | RE |

Define:
- `false_accept = RA`: reference REJECT but judge ACCEPT. This is the dangerous direction for a quality/safety release decision.
- `false_reject = AR`: reference ACCEPT but judge REJECT.
- `evaluated_valid = AA+AR+RA+RR` (non-abstain, non-error adjudicated predictions).
- `eligible_total = AA+AR+A?+AE+RA+RR+R?+RE` (adjudicated references).
- `coverage = evaluated_valid/eligible_total`.
- `conditional_accuracy = (AA+RR)/evaluated_valid`, undefined if zero. **Never label this just `accuracy` without the conditioning**.
- `all_case_correctness = (AA+RR)/eligible_total`, with ABSTAIN and ERROR counted as not correct for this explicitly defined metric; use separate breakdown so this isn't confused with harmful false decisions.
- `false_accept_rate_on_rejects = RA/(RA+RR)` among answered REJECT-reference cases; **also show `RA/(RA+RR+R?+RE)` as a population-style summary** so coverage cannot hide risks.
- `false_reject_rate_on_accepts = AR/(AA+AR)` among answered ACCEPT-reference cases, alongside abstention/error counts.
- `safe_case_accept_precision = AA/(AA+RA)` (if any predicted ACCEPT), useful but insufficient alone.

Never report undefined as 0. Show `null`, explicit reason and denominators.

## Cohen's kappa on answered cases only
Let `n = AA+AR+RA+RR`. `p_o=(AA+RR)/n`. `p_e=[(AA+AR)(AA+RA)+(RA+RR)(AR+RR)]/n²`. `kappa=(p_o-p_e)/(1-p_e)` when `n>0` and `p_e<1`; undefined otherwise. Always show n, class prevalence, coverage and confusion matrix alongside kappa. Kappa can be misleading on imbalanced datasets.

## Confidence intervals
- For binomial proportions with denominator `n>0`, implement Wilson two-sided 95% interval with `z=1.959963984540054`, center `[(p+z²/(2n))/(1+z²/n)]` and half-width `[z*sqrt(p(1-p)/n + z²/(4n²))/(1+z²/n)]`.
- Don't quote a "95% CI" for Cohen's kappa unless a documented appropriate resampling method is implemented; initial version may report kappa point estimate only.
- Confidence intervals are descriptive for the sample/sampling assumptions; clustered/correlated cases invalidate simple independence assumptions. For reports with repeated variants of a case, use case-level cluster resampling where implemented and distinguish from independent-case Wilson intervals.
- Stratified/targeted samples do not automatically justify population-level generalization. Mark sampling design and weighting explicitly.

## Bias/probe metrics
- **Paired inconsistency rate:** among independently validated meaning-preserving pairs, number with divergent judge decisions / total eligible pairs. Count abstains/errors separately and include both orderings when relevant.
- **Attempt validity rate:** valid attempted probes / total submitted probes.
- **Baseline-correct conditional attack success:** validated successful adversarial cases / valid attack cases whose baseline clean prediction was correct. Also report unconditional validated success / all valid probes.
- **Fixed budget:** attempts, calls, model tokens, time, cost and human validity-review minutes. Compare matched attacks at the same budget.
- A response flip is not success if the authoritative reference changed or parser merely broke, unless a separate availability threat had been declared beforehand.

## Golden numerical tests (independent hand calculations)
Fixture 1: reference `[ACCEPT,ACCEPT,REJECT,REJECT]`, prediction `[ACCEPT,REJECT,ACCEPT,REJECT]` => AA=1, AR=1, RA=1, RR=1, evaluated_valid=4, coverage=1, conditional_accuracy=0.5, `kappa=0`, false_accept_rate_on_rejects=0.5.

Fixture 2: reference `[ACCEPT,REJECT,REJECT,ACCEPT]`, prediction `[ACCEPT,REJECT,ABSTAIN,ERROR]` => AA=1, RR=1, R?=1, AE=1, eligible_total=4, evaluated_valid=2, coverage=0.5, conditional_accuracy=1.0, all_case_correctness=0.5, false_accept=0. This proves why a seemingly perfect conditional accuracy can conceal low coverage.

Fixture 3: all references ACCEPT and all predictions ACCEPT => agreement=1, kappa undefined because expected agreement=1 (do not force 1). Empty dataset => undefined metrics with reason and no release PASS.

Fixture 4: no false accepts among 20 independent REJECT-reference cases => observed false_accept_rate=0 but Wilson 95% upper bound is **nonzero**. Never assert zero risk. Validate actual numeric upper bound against an independently calculated test (approximately 0.1611 for n=20).

## Release gate and uncertainty
Define thresholds in YAML with minimum class counts and conservative confidence-bound checks. For example, candidate `PASS` requires `minimum_reject_cases >= 50` and false-accept Wilson *upper* <= stated policy limit, plus clean-task coverage above policy min. These numbers are **illustrative product policy**, not a validated industry safety requirement. Because 50 cases alone cannot establish very rare failure rates, high-stakes decisions must normally be `REVIEW_REQUIRED` until stronger evidence exists.

## Known statistical traps to test
Macro versus micro averaging, class imbalance, label disagreement, sampling bias, distribution shift, selective abstention, pair dependence, multiple testing, model-version drift, selective reporting, prompt tuning on holdout, insufficient rare-failure samples, token/cost budget confounders.
