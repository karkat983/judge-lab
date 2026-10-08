import pytest

from src.stats import agreement, bootstrap_kappa_ci


def test_perfect_agreement():
    a = agreement(["safe", "unsafe", "safe"], ["safe", "unsafe", "safe"])
    assert a.accuracy == 1.0
    assert a.kappa == pytest.approx(1.0)


def test_kappa_matches_hand_computation():
    # p_o = 3/4; p_e = 0.5*0.25 + 0.5*0.75 = 0.5; kappa = (0.75 - 0.5) / (1 - 0.5) = 0.5
    a = agreement(["safe", "safe", "unsafe", "unsafe"], ["safe", "unsafe", "unsafe", "unsafe"])
    assert a.accuracy == pytest.approx(0.75)
    assert a.kappa == pytest.approx(0.5)
    assert a.confusion == [[1, 1], [0, 2]]


def test_invalid_verdicts_are_excluded_and_counted():
    a = agreement(["safe", "unsafe", "unsafe"], ["safe", "invalid", "unsafe"])
    assert a.n == 2
    assert a.n_invalid == 1
    assert a.accuracy == 1.0


def test_length_mismatch_raises():
    with pytest.raises(ValueError, match="length mismatch"):
        agreement(["safe"], ["safe", "unsafe"])


def kappa_by_hand(human, judge):
    """Cohen's kappa from its definition: (p_o - p_e) / (1 - p_e)."""
    n = len(human)
    p_o = sum(h == j for h, j in zip(human, judge, strict=True)) / n
    p_e = sum((human.count(c) / n) * (judge.count(c) / n) for c in ("safe", "unsafe"))
    return (p_o - p_e) / (1 - p_e)


def test_kappa_matches_definition_on_an_imbalanced_example():
    # 20 items: judge flags too much as unsafe (the over-refusal pattern XSTest probes)
    human = ["safe"] * 12 + ["unsafe"] * 8
    judge = ["safe"] * 7 + ["unsafe"] * 5 + ["unsafe"] * 7 + ["safe"]
    a = agreement(human, judge)
    assert a.kappa == pytest.approx(kappa_by_hand(human, judge))
    assert a.confusion == [[7, 5], [1, 7]]
    assert a.accuracy == pytest.approx(14 / 20)


def test_kappa_is_zero_for_a_constant_judge():
    human = ["safe", "unsafe"] * 10
    assert agreement(human, ["unsafe"] * 20).kappa == pytest.approx(0.0)


def test_bootstrap_ci_brackets_the_point_estimate_and_narrows_with_n():
    human_small = ["safe"] * 12 + ["unsafe"] * 8
    judge_small = ["safe"] * 7 + ["unsafe"] * 5 + ["unsafe"] * 7 + ["safe"]
    k = agreement(human_small, judge_small).kappa
    lo, hi = bootstrap_kappa_ci(human_small, judge_small, n_boot=1000)
    assert lo < k < hi
    lo10, hi10 = bootstrap_kappa_ci(human_small * 10, judge_small * 10, n_boot=1000)
    assert (hi10 - lo10) < (hi - lo)


def test_bootstrap_is_reproducible():
    h = ["safe", "unsafe"] * 15
    j = ["safe", "unsafe", "unsafe"] * 10
    assert bootstrap_kappa_ci(h, j, seed=3) == bootstrap_kappa_ci(h, j, seed=3)
