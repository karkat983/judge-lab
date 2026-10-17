"""Independent numerical sample audit using retained sklearn/SciPy development dependencies."""

import itertools

import pytest
from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix

from judge_lab.metrics import binary_statistics, wilson


def test_all_small_confusions_against_sklearn():
    for aa, ar, ra, rr in itertools.product(range(4), repeat=4):
        n = aa + ar + ra + rr
        if not n:
            continue
        refs = ("ACCEPT",) * (aa + ar) + ("REJECT",) * (ra + rr)
        preds = ("ACCEPT",) * aa + ("REJECT",) * ar + ("ACCEPT",) * ra + ("REJECT",) * rr
        stats = binary_statistics(refs, preds)
        matrix = confusion_matrix(refs, preds, labels=["ACCEPT", "REJECT"])
        assert matrix.tolist() == [[aa, ar], [ra, rr]]
        assert stats.metrics["conditional_accuracy"].value == pytest.approx(accuracy_score(refs, preds))
        if stats.kappa is not None:
            assert stats.kappa == pytest.approx(cohen_kappa_score(refs, preds, labels=["ACCEPT", "REJECT"]))
        else:
            assert len(set(refs) | set(preds)) == 1


def test_wilson_against_scipy_score_interval():
    for n in (1, 2, 20, 50, 200, 10000):
        for k in {0, n // 4, n // 2, n}:
            interval = binomtest(k, n).proportion_ci(confidence_level=0.95, method="wilson")
            assert wilson(k, n) == pytest.approx((interval.low, interval.high), abs=1e-12)
