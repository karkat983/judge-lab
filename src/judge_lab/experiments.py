"""Frozen, resource-matched descriptive comparisons; never infer product superiority."""

import argparse
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from judge_lab.artifacts import write_bundle
from judge_lab.configuration import read_config
from judge_lab.contracts import ContractError, Count, Digest, Identifier, Nonnegative, Versioned
from judge_lab.reports import CalibrationReport, read_report, verify_report
from judge_lab.serialization import canonical_bytes, digest


class ResourceBudget(Versioned):
    model_calls: Count
    reviewer_minutes: Nonnegative
    tokens: Count
    cost_usd: Nonnegative


class ExperimentPlan(Versioned):
    experiment_id: Identifier
    baseline_200_report_digest: Digest
    judge_spec_digest: Digest
    rubric_digest: Digest
    holdout_dataset_digest: Digest
    development_family_refs: tuple[Digest, ...]
    holdout_family_refs: Annotated[tuple[Digest, ...], Field(min_length=1)]
    comparator: Literal["conventional_fixed", "random_review"]
    budget_per_arm: ResourceBudget
    severity_protocol: Literal["material-or-critical-v1"]
    analysis: Literal["paired-family-descriptive-v1"]
    stop_rule: Literal["fixed-budget-no-optional-stopping"]
    seed: Count


class VerifiedFinding(Versioned):
    case_ref: Digest
    family_ref: Digest
    failure_type: Identifier
    severity: Literal["MATERIAL", "CRITICAL"]
    independent_reviewer_refs: Annotated[tuple[Digest, ...], Field(min_length=2)]
    evidence_digest: Digest


class ArmLedger(Versioned):
    plan_digest: Digest
    report_digest: Digest
    method: Literal["conventional_fixed", "random_review", "judge_lab"]
    resources: ResourceBudget
    verified_findings: tuple[VerifiedFinding, ...]
    invalid_probes: Count
    false_alarms: Count


def _finding_keys(report: CalibrationReport, ledger: ArmLedger) -> set[tuple[str, str]]:
    by_case = {o.case_ref: o for o in report.observations}
    keys: set[tuple[str, str]] = set()
    for finding in ledger.verified_findings:
        observation = by_case.get(finding.case_ref)
        if (
            observation is None
            or observation.reference != "REJECT"
            or observation.verdict != "ACCEPT"
            or observation.family_ref != finding.family_ref
            or len(set(finding.independent_reviewer_refs)) < 2
        ):
            raise ContractError("INTEGRITY_ERROR")
        # Multiple variants/reviewer entries cannot inflate the same family/failure-type discovery.
        keys.add((finding.family_ref, finding.failure_type))
    return keys


def compare(
    plan: ExperimentPlan,
    baseline200: CalibrationReport,
    baseline: CalibrationReport,
    candidate: CalibrationReport,
    baseline_ledger: ArmLedger,
    candidate_ledger: ArmLedger,
) -> dict[str, object]:
    for report in (baseline200, baseline, candidate):
        verify_report(report)
        if (
            report.run_manifest.judge_spec_digest != plan.judge_spec_digest
            or report.run_manifest.rubric_digest != plan.rubric_digest
        ):
            raise ContractError("INTEGRITY_ERROR")
    base_families = {o.family_ref for o in baseline200.observations}
    holdout = set(plan.holdout_family_refs)
    development = set(plan.development_family_refs)
    if (
        baseline200.report_digest != plan.baseline_200_report_digest
        or len(baseline200.observations) != 200
        or len(base_families) != 200
        or any(o.split != "calibration_200" for o in baseline200.observations)
        or len(holdout) != len(plan.holdout_family_refs)
        or len(development) != len(plan.development_family_refs)
        or holdout & (development | base_families)
    ):
        raise ContractError("INTEGRITY_ERROR")
    for report, ledger, method in (
        (baseline, baseline_ledger, plan.comparator),
        (candidate, candidate_ledger, "judge_lab"),
    ):
        if (
            report.run_manifest.dataset_digest != plan.holdout_dataset_digest
            or {o.family_ref for o in report.observations} != holdout
            or any(o.split != "heldout_test" for o in report.observations)
            or ledger.plan_digest != digest(plan)
            or ledger.report_digest != report.report_digest
            or ledger.method != method
            or ledger.resources != plan.budget_per_arm
            or ledger.resources.model_calls < 200 + len(report.observations)
        ):
            raise ContractError("INTEGRITY_ERROR")
        observations = (*baseline200.observations, *report.observations)
        costs = [o.estimated_cost_usd for o in observations]
        if (
            any(c is None for c in costs)
            or sum(c for c in costs if c is not None) > ledger.resources.cost_usd
            or sum(o.input_tokens + o.output_tokens for o in observations) > ledger.resources.tokens
        ):
            raise ContractError("INTEGRITY_ERROR")
    # The MVP compares review workflows over the same frozen subject observations.
    # Different transformed datasets require a future, reviewed paired mapping contract.
    if (
        baseline.run_manifest.dataset_manifest_digest != candidate.run_manifest.dataset_manifest_digest
        or baseline.run_manifest.split_digest != candidate.run_manifest.split_digest
        or baseline.run_manifest.adapter_version != candidate.run_manifest.adapter_version
        or baseline.run_manifest.label_protocol_revision != candidate.run_manifest.label_protocol_revision
        or baseline.observations != candidate.observations
    ):
        raise ContractError("INTEGRITY_ERROR")
    b0, b1 = _finding_keys(baseline, baseline_ledger), _finding_keys(candidate, candidate_ledger)
    minutes = plan.budget_per_arm.reviewer_minutes
    synthetic = any(r.evidence_status != "HUMAN_ADJUDICATED" for r in (baseline200, baseline, candidate))
    arms = []
    for report, ledger, findings in ((baseline, baseline_ledger, b0), (candidate, candidate_ledger, b1)):
        arms.append(
            {
                "method": ledger.method,
                "report_digest": report.report_digest,
                "unique_verified_failures": len(findings),
                "unique_failures_per_reviewer_hour": 60 * len(findings) / minutes if minutes else None,
                "unique_failures_per_100_cases": 100 * len(findings) / len(report.observations),
                "resources": ledger.resources.model_dump(mode="json"),
                "false_alarms": ledger.false_alarms,
                "invalid_probes": ledger.invalid_probes,
                "clean_case_coverage": report.statistics.metrics["coverage"].model_dump(mode="json"),
            }
        )
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "status": "SYNTHETIC_CODE_VALIDATION" if synthetic else "DESCRIPTIVE_ONLY",
        "plan_digest": digest(plan),
        "baseline_200_report_digest": baseline200.report_digest,
        "baseline_ledger_digest": digest(baseline_ledger),
        "candidate_ledger_digest": digest(candidate_ledger),
        "arms": arms,
        "additional_unique_failures": len(b1 - b0),
        "net_unique_difference": len(b1) - len(b0),
        "incremental_unique_per_reviewer_hour": 60 * (len(b1) - len(b0)) / minutes if minutes else None,
        "paired_families": [
            {
                "family_ref": f,
                "baseline_discovery": any(k[0] == f for k in b0),
                "candidate_discovery": any(k[0] == f for k in b1),
            }
            for f in sorted(holdout)
        ],
        "uncertainty": "No discovery-rate CI: reviewed selections are not independent random samples.",
        "conclusion": "INCONCLUSIVE",
        "superiority_demonstrated": False,
        "limitations": [
            "Reviewer identities, budgets and preregistration need independent authentication.",
            "Matched resources are supplied ledgers, not independently timed observations.",
            "This runner compares review of identical frozen cases; novel probe sets are deferred.",
            "Preserve zero/negative differences; no optional stopping or significance claim.",
        ],
    }
    return {**payload, "comparison_digest": digest(payload)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plan", "baseline200", "baseline", "candidate", "baseline-ledger", "candidate-ledger"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    inputs = (
        args.plan,
        args.baseline200,
        args.baseline,
        args.candidate,
        args.baseline_ledger,
        args.candidate_ledger,
    )
    try:
        if not any(inputs):
            report = {
                "schema_version": "1.0",
                "status": "NOT_PERFORMED",
                "reason": "NO_EMPIRICAL_INPUTS",
                "superiority_demonstrated": False,
            }
            write_bundle(args.out, {"comparison.json": canonical_bytes(report)})
            print("NOT_PERFORMED")
            return 4
        if not all(inputs):
            raise ContractError("INVALID_INPUT")
        result = compare(
            read_config(ExperimentPlan, args.plan),
            read_report(args.baseline200),
            read_report(args.baseline),
            read_report(args.candidate),
            read_config(ArmLedger, args.baseline_ledger),
            read_config(ArmLedger, args.candidate_ledger),
        )
        write_bundle(args.out, {"comparison.json": canonical_bytes(result)})
        print(result["status"])
        return 0
    except (ContractError, OSError, ValueError):
        print("INVALID_COMPARISON")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
