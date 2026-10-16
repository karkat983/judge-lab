# Phase 03 — calibration mathematics

Added `metrics.py` pure count/denominator calculations, conditional and unconditional
rates, answered-case kappa with null reasons, Wilson 95% intervals, family/defect
slices and small-sample flags. Slice keys are hashed to avoid emitting source strings.
Repeated incident families suppress naive independent-binomial intervals and remain
explicitly marked correlated; cluster bootstrap is not claimed.

Validation: six new tests passed (exit 0), Ruff on new files passed (exit 0), mypy
passed (exit 0). Tests implement all four specification goldens, independently
tabulated Wilson endpoints, empty/all-abstain/error/one-class behavior, the legacy
hand-calculated imbalanced kappa example, mismatch rejection and correlated cases.
No new numerical library dependency was needed. Existing legacy math/tests retained.

Actual synthetic API demonstration: coverage 0.8, conditional accuracy 1.0, written
to ignored `runs/phase03-metrics.json` (exit 0). These are constructed fixture outcomes,
not model performance. Point kappa only; no unsupported kappa confidence interval.
Engineering gate complete. Next authorized phase: 04.
