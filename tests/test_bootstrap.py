"""Statistical check of the bootstrap CI: does a nominal 90% interval cover the true kappa?"""
import numpy as np
import pytest

from src.stats import bootstrap_kappa_ci

# Population: 55% safe; the judge agrees 85% of the time on each class.
P_SAFE, P_AGREE = 0.55, 0.85


def true_kappa() -> float:
    p_o = P_AGREE
    judge_safe = P_SAFE * P_AGREE + (1 - P_SAFE) * (1 - P_AGREE)
    p_e = P_SAFE * judge_safe + (1 - P_SAFE) * (1 - judge_safe)
    return (p_o - p_e) / (1 - p_e)


def draw(n: int, rng) -> tuple[list[str], list[str]]:
    human = np.where(rng.random(n) < P_SAFE, "safe", "unsafe")
    flip = rng.random(n) > P_AGREE
    judge = np.where(flip, np.where(human == "safe", "unsafe", "safe"), human)
    return list(human), list(judge)


@pytest.mark.slow
def test_ci_covers_true_kappa_at_about_the_nominal_rate():
    rng = np.random.default_rng(42)
    k = true_kappa()
    hits = 0
    trials = 60
    for t in range(trials):
        human, judge = draw(200, rng)
        lo, hi = bootstrap_kappa_ci(human, judge, n_boot=300, level=0.90, seed=t)
        hits += lo <= k <= hi
    assert 0.78 <= hits / trials <= 0.98        # nominal 0.90; the band allows for 60 trials


def test_invalid_verdicts_are_ignored_and_too_few_raise():
    lo, hi = bootstrap_kappa_ci(["safe", "unsafe"] * 10, ["safe", "unsafe"] * 9 + ["invalid", "invalid"])
    assert lo == pytest.approx(1.0) and hi == pytest.approx(1.0)
    with pytest.raises(ValueError):
        bootstrap_kappa_ci(["safe", "safe"], ["invalid", "invalid"])
