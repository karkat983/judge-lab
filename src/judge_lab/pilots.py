"""Private pilot records and content-minimized summaries. No recruitment or network access."""

import argparse
from datetime import date as CalendarDate
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import field_validator, model_validator

from judge_lab.artifacts import write_bundle
from judge_lab.configuration import read_config
from judge_lab.contracts import ContractError, Count, Digest, Identifier, Nonnegative, Text, Versioned
from judge_lab.serialization import canonical_bytes, digest


class PilotRecord(Versioned):
    pilot_id: Identifier
    status: Literal["NOT_STARTED", "CONSENTED", "COMPLETED", "WITHDRAWN"]
    evidence_kind: Literal["REAL", "SYNTHETIC_TEST"]
    role: Text | None = None
    industry: Text | None = None
    consent_record: Digest | None = None
    dataset_permissions: Digest | None = None
    retain_summary_consent: bool = False
    workflow_before: Text | None = None
    task_minutes: Nonnegative | None = None
    setup_minutes: Nonnegative | None = None
    labels_used: Count | None = None
    baseline_findings_confirmed: Count | None = None
    judge_lab_findings_confirmed: Count | None = None
    invalid_findings: Count | None = None
    rejected_findings: Count | None = None
    incremental_reviewer_minutes: Nonnegative | None = None
    pricing_signal: Text | None = None
    qualitative_feedback: Text | None = None
    observed_decision_change: bool | None = None
    date: CalendarDate | None = None
    source_of_claim: Literal["OBSERVED_SESSION", "TEST_FIXTURE"] | None = None
    supporting_artifact_digests: tuple[Digest, ...] = ()

    @field_validator("date", mode="before")
    @classmethod
    def iso_date(cls, value: Any) -> CalendarDate | None:
        if value is None or type(value) is CalendarDate:
            return value
        if isinstance(value, str):
            try:
                parsed = CalendarDate.fromisoformat(value)
                if parsed.isoformat() == value:
                    return parsed
            except ValueError:
                pass
        raise ContractError("INVALID_INPUT")

    @model_validator(mode="after")
    def complete_records_have_evidence(self) -> Self:
        if self.status in ("CONSENTED", "COMPLETED") and (
            self.consent_record is None or self.dataset_permissions is None
        ):
            raise ContractError("INVALID_INPUT")
        if self.status == "COMPLETED":
            required = (
                self.role,
                self.consent_record,
                self.dataset_permissions,
                self.workflow_before,
                self.task_minutes,
                self.setup_minutes,
                self.labels_used,
                self.baseline_findings_confirmed,
                self.judge_lab_findings_confirmed,
                self.invalid_findings,
                self.rejected_findings,
                self.incremental_reviewer_minutes,
                self.pricing_signal,
                self.qualitative_feedback,
                self.observed_decision_change,
                self.date,
                self.source_of_claim,
            )
            if (
                any(v is None for v in required)
                or not self.retain_summary_consent
                or not self.supporting_artifact_digests
            ):
                raise ContractError("INVALID_INPUT")
            if (self.evidence_kind == "REAL") != (self.source_of_claim == "OBSERVED_SESSION"):
                raise ContractError("INVALID_INPUT")
        return self


def summarize(records: tuple[PilotRecord, ...]) -> dict[str, object]:
    if len(records) > 1000 or len({r.pilot_id for r in records}) != len(records):
        raise ContractError("INVALID_INPUT")
    completed = tuple(r for r in records if r.status == "COMPLETED" and r.evidence_kind == "REAL")
    payload: dict[str, object] = {
        "schema_version": "1.0",
        "real_completed_records": len(completed),
        "five_completed_records": len(completed) >= 5,
        "status": "NO_REAL_PILOT_DATA"
        if not completed
        else "SUPPLIED_RECORDS_REQUIRE_INDEPENDENT_VERIFICATION",
        "total_records": len(records),
        "synthetic_records_excluded": sum(r.evidence_kind == "SYNTHETIC_TEST" for r in records),
        "withdrawn_records_excluded": sum(r.status == "WITHDRAWN" for r in records),
        "not_completed_records": sum(r.status != "COMPLETED" for r in records),
        "completed_record_digests": [digest(r) for r in completed],
        "observed_decision_changes": sum(r.observed_decision_change is True for r in completed),
        "task_minutes": sum(r.task_minutes or 0.0 for r in completed),
        "setup_minutes": sum(r.setup_minutes or 0.0 for r in completed),
        "limitations": [
            "Record validation cannot authenticate participants, consent or observed claims.",
            "Five sessions are early usability evidence, not statistical or market validation.",
            "No participant statements, identities or raw data appear in this summary.",
        ],
    }
    return {**payload, "summary_digest": digest(payload)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = summarize(tuple(read_config(PilotRecord, path) for path in args.records))
        write_bundle(args.out, {"pilot_summary.json": canonical_bytes(result)})
        print(result["status"])
        return 0
    except (ContractError, OSError, ValueError):
        print("INVALID_PILOT_RECORDS")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
