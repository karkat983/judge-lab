import pytest

from judge_lab.contracts import ContractError
from judge_lab.gates import CriticalFinding, GateEvidence, GatePolicy, evaluate_gate
from judge_lab.reports import CalibrationReport
from judge_lab.serialization import canonical_bytes, decode_model, digest


def policy_for(report, **changes):
    return decode_model(
        GatePolicy,
        canonical_bytes(
            dict(
                schema_version="1.0",
                policy_id="test-only",
                policy_revision="v1",
                required_dataset_split="heldout_test",
                minimum_reference_reject_cases=30,
                minimum_reference_accept_cases=30,
                minimum_answer_coverage=0.95,
                maximum_false_accept_wilson_upper=0.1,
                maximum_false_reject_wilson_upper=None,
                no_unresolved_critical_case=True,
                critical_finding_behavior="FAIL",
                require_probe_review=True,
                human_override_required=True,
                expected_judge_spec_digest=report.run_manifest.judge_spec_digest,
                expected_rubric_digest=report.run_manifest.rubric_digest,
                expected_dataset_digest=report.run_manifest.dataset_digest,
                expected_report_digest=None,
                baseline_report_digest=None,
            )
            | changes
        ),
    )


def evidence_for(report, policy, **changes):
    return decode_model(
        GateEvidence,
        canonical_bytes(
            dict(
                schema_version="1.0",
                report_digest=report.report_digest,
                policy_digest=digest(policy),
                critical_review_complete=True,
                critical_findings=[],
                probe_review_status="COMPLETED",
                probe_report_digest=digest("test-only-probe-attestation"),
                human_approval_record_digest=digest("test-only-approval"),
                independent_reviewer_ref=digest("test-reviewer"),
            )
            | changes
        ),
    )


@pytest.mark.parametrize(
    "n,split,evidence,reason",
    [
        (100, "heldout_test", "SYNTHETIC", "SYNTHETIC_EVIDENCE"),
        (100, "development", "HUMAN_ADJUDICATED", "HOLDOUT_MISSING"),
        (20, "heldout_test", "HUMAN_ADJUDICATED", "INSUFFICIENT_ANSWERED_CLASS_COUNTS"),
    ],
)
def test_inadequate_evidence_never_passes(report_factory, n, split, evidence, reason):
    report = report_factory(n, split, evidence)
    result = evaluate_gate(report, policy_for(report))
    assert result.status == "INCONCLUSIVE" and reason in result.reasons and result.exit_code == 4


def test_zero_errors_can_fail_uncertainty(report_factory):
    report = report_factory(100, evidence="HUMAN_ADJUDICATED")
    result = evaluate_gate(report, policy_for(report, maximum_false_accept_wilson_upper=0.01))
    assert result.status == "FAIL" and result.exit_code == 1


def test_scoped_pass_requires_bound_attestations(report_factory):
    report = report_factory(100, evidence="HUMAN_ADJUDICATED")
    policy = policy_for(report)
    assert evaluate_gate(report, policy).status == "INCONCLUSIVE"
    evidence = evidence_for(report, policy)
    assert evaluate_gate(report, policy, evidence).status == "PASS"
    missing = evidence_for(report, policy, human_approval_record_digest=None)
    assert evaluate_gate(report, policy, missing).status == "REVIEW_REQUIRED"
    missing = evidence_for(report, policy, probe_report_digest=None)
    assert evaluate_gate(report, policy, missing).status == "INCONCLUSIVE"
    changed = policy_for(report, policy_revision="v2")
    result = evaluate_gate(report, changed, evidence)
    assert result.status == "ERROR" and result.policy_digest != digest(policy)


def test_critical_finding_fails_even_before_statistics(report_factory):
    report = report_factory(100, evidence="HUMAN_ADJUDICATED", predictions=("ACCEPT",) * 100)
    policy = policy_for(report)
    o = next(o for o in report.observations if o.reference == "REJECT")
    finding = CriticalFinding(
        schema_version="1.0",
        case_ref=o.case_ref,
        status="VERIFIED",
        reviewer_refs=(digest("test-1"), digest("test-2")),
        evidence_digest=digest("test-evidence"),
    )
    evidence = evidence_for(report, policy, critical_findings=[finding.model_dump(mode="json")])
    assert evaluate_gate(report, policy, evidence).status == "FAIL"


def test_tamper_and_injected_authority_reject(report_factory):
    report = report_factory(100)
    policy = policy_for(report)
    report.statistics.counts["RA"] += 1
    assert evaluate_gate(report, policy).status == "ERROR"
    data = report.model_dump(mode="json") | {"decision": "PASS"}
    with pytest.raises(ContractError):
        decode_model(CalibrationReport, canonical_bytes(data), max_bytes=16 * 1024 * 1024)
    with pytest.raises(ContractError):
        decode_model(GatePolicy, canonical_bytes(policy.model_dump(mode="json") | {"override": True}))


def test_coverage_not_conditional_accuracy_controls_gate(report_factory):
    # Both classes retain >30 answered cases, yet coverage is only 80%.
    # Use original cyclic label order for the generated cases.
    refs = (
        "ACCEPT",
        "REJECT",
        "REJECT",
        "REJECT",
        "REJECT",
        "ACCEPT",
        "ACCEPT",
        "REJECT",
        "ACCEPT",
        "ACCEPT",
    )
    predictions = tuple(refs[i % 10] if i % 5 else "ABSTAIN" for i in range(100))
    report = report_factory(100, evidence="HUMAN_ADJUDICATED", predictions=predictions)
    assert report.statistics.metrics["conditional_accuracy"].value == 1.0
    result = evaluate_gate(report, policy_for(report))
    assert result.status == "FAIL" and result.reasons == ("ANSWER_COVERAGE_BELOW_POLICY",)


def test_baseline_must_be_comparable(report_factory):
    report = report_factory(100, evidence="HUMAN_ADJUDICATED")
    baseline = report_factory(110, evidence="HUMAN_ADJUDICATED")
    policy = policy_for(report, baseline_report_digest=baseline.report_digest)
    assert evaluate_gate(report, policy).reasons == ("BASELINE_MISSING",)
    assert evaluate_gate(report, policy, baseline=baseline).reasons == ("BASELINE_INCOMPARABLE",)


def test_gate_cli_exit_and_output(report_factory, tmp_path):
    from judge_lab.cli import main

    report = report_factory(10)
    policy = policy_for(report)
    report_path, policy_path = tmp_path / "report.json", tmp_path / "policy.json"
    report_path.write_bytes(canonical_bytes(report))
    policy_path.write_bytes(canonical_bytes(policy))
    assert (
        main(
            [
                "gate",
                "--report",
                str(report_path),
                "--policy",
                str(policy_path),
                "--out",
                str(tmp_path / "gate"),
            ]
        )
        == 4
    )
    assert b'"status":"INCONCLUSIVE"' in (tmp_path / "gate/decision.json").read_bytes()
