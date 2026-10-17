"""Pure conservative policy evaluation. Gate output is scoped evidence, never certification."""

from typing import Annotated, Literal

from pydantic import Field

from judge_lab.contracts import ContractError, Count, Digest, Identifier, Versioned
from judge_lab.reports import CalibrationReport, verify_report
from judge_lab.serialization import canonical_bytes, decode_model, digest

Probability = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
GateStatus = Literal["PASS", "FAIL", "REVIEW_REQUIRED", "INCONCLUSIVE", "ERROR"]
EXIT_CODES = {"PASS": 0, "FAIL": 1, "ERROR": 2, "REVIEW_REQUIRED": 3, "INCONCLUSIVE": 4}


class GatePolicy(Versioned):
    policy_id: Identifier
    policy_revision: Identifier
    required_dataset_split: Literal["heldout_test"]
    minimum_reference_reject_cases: Annotated[int, Field(ge=1)]
    minimum_reference_accept_cases: Annotated[int, Field(ge=1)]
    minimum_answer_coverage: Probability
    maximum_false_accept_wilson_upper: Probability
    maximum_false_reject_wilson_upper: Probability | None
    no_unresolved_critical_case: bool
    critical_finding_behavior: Literal["FAIL", "REVIEW_REQUIRED"]
    require_probe_review: bool
    human_override_required: bool
    expected_judge_spec_digest: Digest | None
    expected_rubric_digest: Digest | None
    expected_dataset_digest: Digest | None
    expected_report_digest: Digest | None
    baseline_report_digest: Digest | None


class CriticalFinding(Versioned):
    case_ref: Digest
    status: Literal["VERIFIED", "UNRESOLVED"]
    reviewer_refs: Annotated[tuple[Digest, ...], Field(min_length=2)]
    evidence_digest: Digest


class GateEvidence(Versioned):
    report_digest: Digest
    policy_digest: Digest
    critical_review_complete: bool
    critical_findings: tuple[CriticalFinding, ...]
    probe_review_status: Literal["COMPLETED", "NOT_PERFORMED", "REVIEW_REQUIRED"]
    probe_report_digest: Digest | None
    human_approval_record_digest: Digest | None
    independent_reviewer_ref: Digest


class GateDecision(Versioned):
    status: GateStatus
    reasons: tuple[Identifier, ...]
    policy_id: Identifier
    policy_revision: Identifier
    policy_digest: Digest
    report_digest: Digest
    evidence_digest: Digest | None
    baseline_report_digest: Digest | None
    decision_digest: Digest
    exit_code: Count
    scope: Literal["policy-specific-evidence-check-not-production-safety"]


def evaluate_gate(
    report: CalibrationReport,
    policy: GatePolicy,
    evidence: GateEvidence | None = None,
    baseline: CalibrationReport | None = None,
) -> GateDecision:
    def decision(status: GateStatus, *reasons: str) -> GateDecision:
        payload = {
            "schema_version": "1.0",
            "status": status,
            "reasons": reasons,
            "policy_id": policy.policy_id,
            "policy_revision": policy.policy_revision,
            "policy_digest": digest(policy),
            "report_digest": report.report_digest,
            "evidence_digest": digest(evidence) if evidence else None,
            "baseline_report_digest": baseline.report_digest if baseline else None,
            "exit_code": EXIT_CODES[status],
            "scope": "policy-specific-evidence-check-not-production-safety",
        }
        return decode_model(GateDecision, canonical_bytes({**payload, "decision_digest": digest(payload)}))

    try:
        verify_report(report, policy.expected_report_digest)
        if evidence and (
            evidence.report_digest != report.report_digest or evidence.policy_digest != digest(policy)
        ):
            return decision("ERROR", "EVIDENCE_BINDING_MISMATCH")
        if evidence:
            by_case = {o.case_ref: o for o in report.observations}
            for finding in evidence.critical_findings:
                if finding.case_ref not in by_case or len(set(finding.reviewer_refs)) < 2:
                    return decision("ERROR", "INVALID_CRITICAL_EVIDENCE")
                o = by_case[finding.case_ref]
                if finding.status == "VERIFIED" and (o.reference != "REJECT" or o.verdict != "ACCEPT"):
                    return decision("ERROR", "INVALID_CRITICAL_EVIDENCE")
            if any(f.status == "VERIFIED" for f in evidence.critical_findings):
                return decision(policy.critical_finding_behavior, "VERIFIED_CRITICAL_FALSE_ACCEPT")
            if policy.no_unresolved_critical_case and evidence.critical_findings:
                return decision("REVIEW_REQUIRED", "UNRESOLVED_CRITICAL_FINDING")
        if policy.baseline_report_digest is not None:
            if baseline is None:
                return decision("INCONCLUSIVE", "BASELINE_MISSING")
            verify_report(baseline, policy.baseline_report_digest)
            keys = (
                "judge_spec_digest",
                "rubric_digest",
                "dataset_digest",
                "dataset_manifest_digest",
                "label_protocol_revision",
                "split_digest",
                "adapter_version",
            )
            if any(getattr(report.run_manifest, k) != getattr(baseline.run_manifest, k) for k in keys):
                return decision("INCONCLUSIVE", "BASELINE_INCOMPARABLE")
        expected = (
            policy.expected_judge_spec_digest,
            policy.expected_rubric_digest,
            policy.expected_dataset_digest,
        )
        actual = (
            report.run_manifest.judge_spec_digest,
            report.run_manifest.rubric_digest,
            report.run_manifest.dataset_digest,
        )
        if any(x is None for x in expected):
            return decision("INCONCLUSIVE", "UNPINNED_SUBJECT_OR_DATA")
        if expected != actual:
            return decision("INCONCLUSIVE", "SUBJECT_OR_DATA_MISMATCH")
        if report.evidence_status != "HUMAN_ADJUDICATED":
            return decision("INCONCLUSIVE", "SYNTHETIC_EVIDENCE")
        if not report.observations or any(
            o.split != policy.required_dataset_split for o in report.observations
        ):
            return decision("INCONCLUSIVE", "HOLDOUT_MISSING")
        stats = report.statistics
        if stats.correlated_cases:
            return decision("INCONCLUSIVE", "CORRELATED_CASES_NO_SUPPORTED_INTERVAL")
        d = stats.denominators
        if (
            d["answered_reject"] < policy.minimum_reference_reject_cases
            or d["answered_accept"] < policy.minimum_reference_accept_cases
        ):
            return decision("INCONCLUSIVE", "INSUFFICIENT_ANSWERED_CLASS_COUNTS")
        coverage = stats.metrics["coverage"].value
        fa = stats.metrics["false_accept_rate_on_rejects"].wilson_95
        fr = stats.metrics["false_reject_rate_on_accepts"].wilson_95
        if coverage is None or fa is None or fr is None:
            return decision("INCONCLUSIVE", "UNDEFINED_REQUIRED_METRIC")
        if coverage < policy.minimum_answer_coverage:
            return decision("FAIL", "ANSWER_COVERAGE_BELOW_POLICY")
        if fa[1] > policy.maximum_false_accept_wilson_upper:
            return decision("FAIL", "FALSE_ACCEPT_WILSON_UPPER_EXCEEDS_POLICY")
        if (
            policy.maximum_false_reject_wilson_upper is not None
            and fr[1] > policy.maximum_false_reject_wilson_upper
        ):
            return decision("FAIL", "FALSE_REJECT_WILSON_UPPER_EXCEEDS_POLICY")
        if evidence is None or not evidence.critical_review_complete:
            return decision("INCONCLUSIVE", "CRITICAL_REVIEW_MISSING")
        if policy.require_probe_review:
            if evidence.probe_review_status == "REVIEW_REQUIRED":
                return decision("REVIEW_REQUIRED", "PROBE_REVIEW_PENDING")
            if evidence.probe_review_status != "COMPLETED" or evidence.probe_report_digest is None:
                return decision("INCONCLUSIVE", "REQUIRED_PROBE_EVIDENCE_MISSING")
        if policy.human_override_required and evidence.human_approval_record_digest is None:
            return decision("REVIEW_REQUIRED", "HUMAN_APPROVAL_RECORD_REQUIRED")
        return decision("PASS", "SCOPED_POLICY_PRECONDITIONS_MET")
    except (ContractError, ValueError, KeyError):
        return decision("ERROR", "INVALID_REPORT_OR_INTEGRITY")
