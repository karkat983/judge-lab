"""Content-minimized, verifiable JSON and escaped standalone HTML evidence reports."""

import html
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field

from judge_lab.contracts import (
    ContractError,
    Digest,
    ErrorKind,
    FrozenModel,
    JudgeResult,
    Nonnegative,
    Outcome,
    ReferenceLabel,
    RunManifest,
    Split,
    Versioned,
)
from judge_lab.load import LoadedDataset, read_bounded
from judge_lab.metrics import Statistics, binary_statistics, calibrate, slice_statistics
from judge_lab.provenance import verify_run_manifest
from judge_lab.runner import validate_results
from judge_lab.serialization import MAX_DOCUMENT_BYTES, canonical_bytes, decode_model, digest


class Observation(FrozenModel):
    case_ref: Digest
    family_ref: Digest
    case_digest: Digest
    split: Split
    reference: ReferenceLabel
    verdict: Outcome
    error_kind: ErrorKind | None
    estimated_cost_usd: Nonnegative | None
    input_tokens: int
    output_tokens: int


class CalibrationReport(Versioned):
    report_digest: Digest
    claim_scope: Literal["security-investigation-judge-on-recorded-dataset"]
    evidence_status: Literal["SYNTHETIC", "HUMAN_ADJUDICATED"]
    run_manifest: RunManifest
    statistics: Statistics
    slice_breakdowns: dict[str, Statistics]
    observations: Annotated[tuple[Observation, ...], Field(max_length=10000)]
    excluded_cases: tuple[str, ...]
    limitations: tuple[str, ...]
    eligible_for_release: Literal[False]


def build_report(dataset: LoadedDataset, results: tuple[JudgeResult, ...],
                 run: RunManifest) -> CalibrationReport:
    ordered = validate_results(dataset, run, results)
    cases = {c.case_id: c for c in dataset.cases}
    observations = tuple(Observation(
        case_ref=digest(r.case_id), family_ref=digest(cases[r.case_id].case_family_id),
        case_digest=r.case_digest, split=cases[r.case_id].split,
        reference=cases[r.case_id].reference_label, verdict=r.verdict, error_kind=r.error_kind,
        estimated_cost_usd=r.estimated_cost_usd, input_tokens=r.input_tokens, output_tokens=r.output_tokens,
    ) for r in ordered)
    payload = {
        "schema_version": "1.0", "claim_scope": "security-investigation-judge-on-recorded-dataset",
        "evidence_status": dataset.manifest.evidence_status,
        "run_manifest": run.model_dump(mode="json"),
        "statistics": calibrate(dataset, ordered, run).model_dump(mode="json"),
        "slice_breakdowns": {k: v.model_dump(mode="json")
                             for k, v in slice_statistics(dataset, ordered, run).items()},
        "observations": [o.model_dump(mode="json") for o in observations], "excluded_cases": [],
        "eligible_for_release": False,
        "limitations": [
            "Synthetic data is code validation, not product effectiveness evidence."
            if dataset.manifest.evidence_status == "SYNTHETIC" else
            "Human-adjudicated status is supplied provenance, not independently certified by this tool.",
            "No universal safety, causal or production guarantee; caller retains release authority.",
            "Wilson intervals assume independent cases; correlated families suppress them.",
            "Digests require trusted expected inputs; they are not authentication signatures.",
        ],
    }
    return decode_model(CalibrationReport, canonical_bytes({**payload, "report_digest": digest(payload)}),
                        max_bytes=MAX_DOCUMENT_BYTES)


def read_report(path: Path) -> CalibrationReport:
    report = decode_model(CalibrationReport, read_bounded(path, MAX_DOCUMENT_BYTES),
                          max_bytes=MAX_DOCUMENT_BYTES)
    verify_report(report)
    return report


def verify_report(report: CalibrationReport, expected_digest: str | None = None) -> None:
    verify_run_manifest(report.run_manifest)
    payload = report.model_dump(mode="json", exclude={"report_digest"})
    if (report.report_digest != digest(payload)
            or (expected_digest and expected_digest != report.report_digest)):
        raise ContractError("INTEGRITY_ERROR")
    if len({o.case_ref for o in report.observations}) != len(report.observations):
        raise ContractError("INTEGRITY_ERROR")
    for o in report.observations:
        if ((o.verdict == "ERROR") != (o.error_kind is not None)
                or o.input_tokens < 0 or o.output_tokens < 0):
            raise ContractError("INTEGRITY_ERROR")
    stats = binary_statistics(tuple(o.reference for o in report.observations),
                              tuple(o.verdict for o in report.observations),
                              tuple(o.family_ref for o in report.observations))
    if stats != report.statistics:
        raise ContractError("INTEGRITY_ERROR")


def render_html(report: CalibrationReport) -> bytes:
    verify_report(report)
    # Escape the complete canonical data, including limitations supplied by imported artifacts.
    data = html.escape(json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False))
    title = "Synthetic demonstration, not product effectiveness evidence" if (
        report.evidence_status == "SYNTHETIC") else "Scoped reliability evidence report"
    page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta http-equiv="Content-Security-Policy" '
            'content="default-src \'none\'; style-src \'unsafe-inline\'">'
            '<title>Judge Lab evidence report</title><style>body{max-width:1000px;margin:2em auto;'
            'font:16px system-ui;padding:1em}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
            f'<h1>{title}</h1><p>Counts and denominators below exactly match report.json.</p>'
            f'<pre>{data}</pre></html>')
    return page.encode("utf-8")


def report_files(report: CalibrationReport) -> dict[str, bytes]:
    return {"report.json": canonical_bytes(report), "report.html": render_html(report),
            "run_manifest.json": canonical_bytes(report.run_manifest)}
