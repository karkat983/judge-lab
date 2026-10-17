from datetime import date
from pathlib import Path

import pytest

from judge_lab.contracts import ContractError
from judge_lab.pilots import PilotRecord, main, summarize
from judge_lab.serialization import canonical_bytes, decode_model, digest


def completed(kind="SYNTHETIC_TEST", pilot_id="test-only"):
    return PilotRecord(
        schema_version="1.0",
        pilot_id=pilot_id,
        status="COMPLETED",
        evidence_kind=kind,
        role="test role",
        consent_record=digest("test-consent"),
        dataset_permissions=digest("test-rights"),
        retain_summary_consent=True,
        workflow_before="test workflow",
        task_minutes=10.0,
        setup_minutes=2.0,
        labels_used=10,
        baseline_findings_confirmed=0,
        judge_lab_findings_confirmed=0,
        invalid_findings=0,
        rejected_findings=0,
        incremental_reviewer_minutes=1.0,
        pricing_signal="TEST ONLY",
        qualitative_feedback="SECRET_CANARY_TEST_ONLY",
        observed_decision_change=False,
        date=date(2026, 1, 1),
        source_of_claim="OBSERVED_SESSION" if kind == "REAL" else "TEST_FIXTURE",
        supporting_artifact_digests=(digest("test-evidence"),),
    )


def test_blank_five_are_not_five_pilots(tmp_path):
    paths = sorted(Path("pilots/templates").glob("P*.json"))
    assert len(paths) == 5
    assert main(["--records", *map(str, paths), "--out", str(tmp_path / "summary")]) == 0
    raw = (tmp_path / "summary/pilot_summary.json").read_text()
    assert '"real_completed_records":0' in raw and "NO_REAL_PILOT_DATA" in raw


def test_synthetic_and_withdrawn_do_not_count():
    synthetic = completed()
    withdrawn = decode_model(
        PilotRecord,
        canonical_bytes(
            {
                **completed("REAL", "withdrawn").model_dump(mode="json"),
                "status": "WITHDRAWN",
                "retain_summary_consent": False,
            }
        ),
    )
    summary = summarize((synthetic, withdrawn))
    assert summary["real_completed_records"] == 0
    assert "SECRET_CANARY" not in str(summary)


def test_five_requires_five_completed_real_declarations():
    # Test-only REAL-shaped records exercise counting, never saved as pilot evidence.
    records = tuple(completed("REAL", f"test-only-{i}") for i in range(5))
    assert not summarize(records[:4])["five_completed_records"]
    assert summarize(records)["five_completed_records"]
    with pytest.raises(ContractError):
        summarize((records[0], records[0]))


@pytest.mark.parametrize(
    "change",
    [
        {"consent_record": None},
        {"dataset_permissions": None},
        {"task_minutes": -1},
        {"task_minutes": float("nan")},
        {"supporting_artifact_digests": []},
        {"retain_summary_consent": False},
        {"source_of_claim": "OBSERVED_SESSION"},
    ],
)
def test_invalid_completion_rejected(change):
    with pytest.raises(ContractError):
        decode_model(PilotRecord, canonical_bytes({**completed().model_dump(mode="json"), **change}))
