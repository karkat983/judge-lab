import pytest

from judge_lab.contracts import ContractError
from judge_lab.metrics import binary_statistics, calibrate, slice_statistics, wilson
from judge_lab.runner import import_predictions
from judge_lab.serialization import canonical_bytes


def test_goldens_and_defined_denominators():
    first = binary_statistics(("ACCEPT", "ACCEPT", "REJECT", "REJECT"),
                              ("ACCEPT", "REJECT", "ACCEPT", "REJECT"))
    assert [first.counts[k] for k in ("AA", "AR", "RA", "RR")] == [1, 1, 1, 1]
    assert first.kappa == 0
    assert first.metrics["conditional_accuracy"].value == 0.5
    second = binary_statistics(("ACCEPT", "REJECT", "REJECT", "ACCEPT"),
                               ("ACCEPT", "REJECT", "ABSTAIN", "ERROR"))
    assert second.denominators["eligible_total"] == 4
    assert second.metrics["conditional_accuracy"].value == 1
    assert second.metrics["coverage"].value == 0.5
    assert second.metrics["all_case_correctness"].value == 0.5
    assert second.counts["R?"] == second.counts["AE"] == 1
    third = binary_statistics(("ACCEPT",) * 4, ("ACCEPT",) * 4)
    assert third.kappa is None and third.kappa_reason == "EXPECTED_AGREEMENT_ONE"
    assert third.metrics["false_accept_rate_on_rejects"].value is None
    # Independent tabulated Wilson endpoints (not computed by copying the production formula).
    assert wilson(0, 20) == pytest.approx((0, 0.1611251580528194))
    assert wilson(5, 10) == pytest.approx((0.236593090512564, 0.763406909487436))
    assert wilson(20, 20) == pytest.approx((0.838874841947181, 1))


@pytest.mark.parametrize("verdict", ["ABSTAIN", "ERROR"])
def test_no_answers_and_empty(verdict):
    stats = binary_statistics(("ACCEPT", "REJECT"), (verdict, verdict))
    assert stats.metrics["coverage"].value == 0
    assert stats.metrics["conditional_accuracy"].value is None
    assert stats.kappa is None
    empty = binary_statistics((), ())
    assert all(m.value is None for m in empty.metrics.values())
    assert b"NaN" not in canonical_bytes(empty)


def test_imbalance_independent_reference_and_correlated_variants():
    # Legacy independently hand-calculated example: [[7,5],[1,7]], po=.7, pe=.48, k=.22/.52.
    stats = binary_statistics(("ACCEPT",) * 12 + ("REJECT",) * 8,
                              ("ACCEPT",) * 7 + ("REJECT",) * 12 + ("ACCEPT",))
    assert stats.kappa == pytest.approx(0.22 / 0.52)
    assert stats.metrics["false_accept_rate_on_rejects"].value == 1 / 8
    correlated = binary_statistics(("REJECT",) * 20, ("REJECT",) * 20, ("same-family",) * 20)
    assert correlated.metrics["false_accept_rate_on_rejects"].wilson_95 is None
    assert correlated.correlated_cases and correlated.independent_families == 1


def test_invalid_and_unmatched_labels():
    for refs, predictions in [(("safe",), ("ACCEPT",)), (("ACCEPT",), ()),
                              (("ACCEPT",), ("maybe",))]:
        with pytest.raises(ContractError):
            binary_statistics(refs, predictions)
    for k, n in [(-1, 2), (3, 2), (1, -1), (True, 2)]:
        with pytest.raises(ContractError):
            wilson(k, n)


def test_bound_calibration_and_slices(dataset, run):
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "examples" / "synthetic_results.jsonl"
    results = import_predictions(path, dataset, run)
    stats = calibrate(dataset, results, run)
    assert stats.metrics["coverage"].value == 0.8
    slices = slice_statistics(dataset, results, run)
    assert all(s.small_sample for s in slices.values())
    assert len([k for k in slices if k.startswith("family:")]) == 10
    with pytest.raises(ContractError):
        calibrate(dataset, results[:-1], run)
