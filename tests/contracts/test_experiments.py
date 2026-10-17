import pytest

from judge_lab.contracts import ContractError
from judge_lab.experiments import ArmLedger, ExperimentPlan, ResourceBudget, VerifiedFinding, compare, main
from judge_lab.serialization import canonical_bytes, decode_model, digest


@pytest.fixture
def comparison_inputs(report_factory):
    b200 = report_factory(200, "calibration_200")
    report = report_factory(10, predictions=("ACCEPT",) * 10)
    budget = ResourceBudget(
        schema_version="1.0", model_calls=210, reviewer_minutes=60.0, tokens=0, cost_usd=0.0
    )
    plan = ExperimentPlan(
        schema_version="1.0",
        experiment_id="test-only",
        baseline_200_report_digest=b200.report_digest,
        judge_spec_digest=report.run_manifest.judge_spec_digest,
        rubric_digest=report.run_manifest.rubric_digest,
        holdout_dataset_digest=report.run_manifest.dataset_digest,
        development_family_refs=(),
        holdout_family_refs=tuple(o.family_ref for o in report.observations),
        comparator="conventional_fixed",
        budget_per_arm=budget,
        severity_protocol="material-or-critical-v1",
        analysis="paired-family-descriptive-v1",
        stop_rule="fixed-budget-no-optional-stopping",
        seed=44,
    )
    b0 = ArmLedger(
        schema_version="1.0",
        plan_digest=digest(plan),
        report_digest=report.report_digest,
        method="conventional_fixed",
        resources=budget,
        verified_findings=(),
        invalid_probes=0,
        false_alarms=0,
    )
    b1 = decode_model(ArmLedger, canonical_bytes({**b0.model_dump(mode="json"), "method": "judge_lab"}))
    return plan, b200, report, report, b0, b1


def test_zero_discovery_valid_and_no_superiority(comparison_inputs):
    output = compare(*comparison_inputs)
    assert output["net_unique_difference"] == 0
    assert output["status"] == "SYNTHETIC_CODE_VALIDATION"
    assert not output["superiority_demonstrated"]


def test_negative_result_preserved_and_findings_deduplicated(comparison_inputs):
    plan, b200, b0, b1, l0, l1 = comparison_inputs
    observation = next(o for o in b0.observations if o.reference == "REJECT")
    finding = VerifiedFinding(
        schema_version="1.0",
        case_ref=observation.case_ref,
        family_ref=observation.family_ref,
        failure_type="prohibited-action",
        severity="MATERIAL",
        independent_reviewer_refs=(digest("test-reviewer-1"), digest("test-reviewer-2")),
        evidence_digest=digest("test-only-declaration"),
    )
    l0 = decode_model(
        ArmLedger,
        canonical_bytes(
            {**l0.model_dump(mode="json"), "verified_findings": [finding.model_dump(mode="json")] * 2}
        ),
    )
    output = compare(plan, b200, b0, b1, l0, l1)
    assert output["net_unique_difference"] == -1
    assert output["incremental_unique_per_reviewer_hour"] == -1.0


@pytest.mark.parametrize(
    "field,value",
    [
        ("judge_spec_digest", digest("different")),
        ("rubric_digest", digest("different")),
        ("holdout_dataset_digest", digest("different")),
    ],
)
def test_incompatible_comparison_rejected(comparison_inputs, field, value):
    plan, *rest = comparison_inputs
    changed = decode_model(ExperimentPlan, canonical_bytes({**plan.model_dump(mode="json"), field: value}))
    with pytest.raises(ContractError):
        compare(changed, *rest)


def test_unequal_budget_and_contamination_reject(comparison_inputs):
    plan, b200, b0, b1, l0, l1 = comparison_inputs
    bad = decode_model(
        ArmLedger,
        canonical_bytes(
            {
                **l1.model_dump(mode="json"),
                "resources": {**l1.resources.model_dump(mode="json"), "reviewer_minutes": 61.0},
            }
        ),
    )
    with pytest.raises(ContractError):
        compare(plan, b200, b0, b1, l0, bad)
    plan = decode_model(
        ExperimentPlan,
        canonical_bytes(
            {**plan.model_dump(mode="json"), "development_family_refs": [plan.holdout_family_refs[0]]}
        ),
    )
    with pytest.raises(ContractError):
        compare(plan, b200, b0, b1, l0, l1)


def test_no_inputs_records_not_performed(tmp_path):
    assert main(["--out", str(tmp_path / "out")]) == 4
    assert b"NOT_PERFORMED" in (tmp_path / "out/comparison.json").read_bytes()
