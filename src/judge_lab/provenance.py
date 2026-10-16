"""Deterministic run compatibility and result bindings. No execution or cache backend."""

from datetime import datetime

from judge_lab.contracts import (
    Case,
    ContractError,
    JudgeResult,
    JudgeSpec,
    RunEnvironment,
    RunManifest,
)
from judge_lab.load import LoadedDataset, verify_dataset
from judge_lab.serialization import digest


def build_run_manifest(
    dataset: LoadedDataset, spec: JudgeSpec, *, adapter_version: str, run_seed: int,
    environment: RunEnvironment, created_at_utc: datetime,
) -> RunManifest:
    verify_dataset(dataset)
    if any(case.rubric_revision != spec.rubric_revision for case in dataset.cases):
        raise ContractError("INTEGRITY_ERROR")
    identity = {
        "schema_version": "1.0",
        "dataset_digest": dataset.manifest.sha256,
        "dataset_manifest_digest": digest(dataset.manifest),
        "label_protocol_revision": dataset.manifest.label_protocol_revision,
        "rubric_digest": digest({"revision": spec.rubric_revision, "text": spec.rubric_text}),
        "judge_spec_digest": digest(spec),
        "split_digest": digest([
            {"case_id": c.case_id, "case_family_id": c.case_family_id, "split": c.split}
            for c in sorted(dataset.cases, key=lambda c: c.case_id)
        ]),
        "adapter_version": adapter_version,
        "run_seed": run_seed,
        "environment": environment,
        "limits": spec.limits,
    }
    # Nested models must be serialized before canonical hashing.
    serial = {**identity, "environment": environment.model_dump(mode="json"),
              "limits": spec.limits.model_dump(mode="json")}
    return RunManifest.model_validate({**identity, "run_id": digest(serial),
                                       "created_at_utc": created_at_utc})


def verify_run_manifest(run: RunManifest) -> None:
    identity = run.model_dump(mode="json", exclude={"run_id", "created_at_utc"})
    if run.run_id != digest(identity):
        raise ContractError("INTEGRITY_ERROR")


def require_compatible_run(stored: RunManifest, expected: RunManifest) -> None:
    verify_run_manifest(stored)
    verify_run_manifest(expected)
    if stored.run_id != expected.run_id:
        raise ContractError("INTEGRITY_ERROR")


def verify_result(result: JudgeResult, case: Case, run: RunManifest, dataset: LoadedDataset) -> None:
    """Require trusted expected manifest/dataset, not an arbitrary self-declared result ID."""
    verify_dataset(dataset)
    verify_run_manifest(run)
    if (run.dataset_digest != dataset.manifest.sha256
            or run.dataset_manifest_digest != digest(dataset.manifest)
            or case not in dataset.cases
            or result.case_id != case.case_id or result.case_digest != digest(case)
            or result.judge_spec_digest != run.judge_spec_digest or result.run_id != run.run_id):
        raise ContractError("INTEGRITY_ERROR")

