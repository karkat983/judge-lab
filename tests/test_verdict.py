import pytest

from src.verdict import INVALID, Verdict


def test_valid_and_invalid_verdicts():
    assert Verdict("safe", "benign").valid
    assert not Verdict(INVALID).valid


def test_other_labels_rejected():
    with pytest.raises(ValueError):
        Verdict("maybe")
