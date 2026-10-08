import pytest

from src.stats import agreement


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
