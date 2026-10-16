"""Read-only JSONL ingestion. Fail the entire batch rather than silently drop a label."""

from dataclasses import dataclass, field
from pathlib import Path

from judge_lab.contracts import Case, ContractError, DatasetRevision
from judge_lab.serialization import MAX_RECORD_BYTES, canonical_bytes, decode_model, digest

MAX_DATASET_BYTES = 16 * 1024 * 1024
MAX_CASES = 10_000


@dataclass(frozen=True)
class LoadedDataset:
    manifest: DatasetRevision = field(repr=False)
    cases: tuple[Case, ...] = field(repr=False)

    def summary(self) -> dict[str, str | int]:
        """Safe default inspection output: no case text, IDs, annotations or source strings."""
        verify_dataset(self)
        return {"schema_version": "1.0", "case_count": len(self.cases),
                "dataset_digest": self.manifest.sha256,
                "evidence_status": self.manifest.evidence_status}


def validate_cases(cases: tuple[Case, ...]) -> tuple[Case, ...]:
    if not cases or len(cases) > MAX_CASES:
        raise ContractError("INVALID_INPUT")
    ids: set[str] = set()
    families: dict[str, str] = {}
    for case in cases:
        if case.case_id in ids:
            raise ContractError("INVALID_INPUT")
        ids.add(case.case_id)
        if case.case_family_id in families and families[case.case_family_id] != case.split:
            raise ContractError("INVALID_INPUT")
        families[case.case_family_id] = case.split
    return tuple(sorted(cases, key=lambda case: case.case_id))


def dataset_digest(cases: tuple[Case, ...]) -> str:
    ordered = validate_cases(cases)
    return digest([case.model_dump(mode="json") for case in ordered])


def dataset_jsonl(cases: tuple[Case, ...]) -> bytes:
    return b"\n".join(canonical_bytes(case) for case in validate_cases(cases)) + b"\n"


def read_bounded(path: Path, limit: int) -> bytes:
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
    except OSError:
        raise ContractError("INVALID_INPUT") from None
    if len(raw) > limit:
        raise ContractError("INPUT_TOO_LARGE")
    return raw


def load_cases(path: Path) -> tuple[Case, ...]:
    raw = read_bounded(path, MAX_DATASET_BYTES)
    lines = raw.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
    if len(lines) > MAX_CASES:
        raise ContractError("INPUT_TOO_LARGE")
    return validate_cases(tuple(decode_model(Case, line) for line in lines))


def verify_dataset(dataset: LoadedDataset) -> None:
    if dataset.manifest.sha256 != dataset_digest(dataset.cases):
        raise ContractError("INTEGRITY_ERROR")


def load_dataset(path: Path, manifest_path: Path) -> LoadedDataset:
    manifest = decode_model(DatasetRevision, read_bounded(manifest_path, MAX_RECORD_BYTES))
    dataset = LoadedDataset(manifest=manifest, cases=load_cases(path))
    verify_dataset(dataset)
    return dataset
