"""Frozen family-level baseline selection and human adjudication import; no auto-labeling."""

import argparse
import json
import random
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from judge_lab.artifacts import write_bundle
from judge_lab.configuration import read_config
from judge_lab.contracts import (
    Case,
    ContractError,
    Count,
    Digest,
    Identifier,
    ReferenceLabel,
    RunManifest,
    Versioned,
)
from judge_lab.load import MAX_DATASET_BYTES, LoadedDataset, load_dataset, read_bounded, verify_dataset
from judge_lab.reports import CalibrationReport, build_report, report_files
from judge_lab.runner import import_predictions
from judge_lab.serialization import canonical_bytes, decode_model, digest


class Adjudication(Versioned):
    case_id: Identifier
    case_digest: Digest
    reviewer_ids: Annotated[tuple[Identifier, ...], Field(min_length=2, max_length=10)]
    reviewer_labels: tuple[ReferenceLabel, ...]
    status: Literal["AGREED", "ADJUDICATED", "DISPUTED"]
    final_label: ReferenceLabel | None
    adjudicator_id: Identifier | None
    independent_of_judge: Literal[True]
    frozen: Literal[True]
    source: Literal["HUMAN"]

    @model_validator(mode="after")
    def consistency(self) -> Self:
        if len(set(self.reviewer_ids)) != len(self.reviewer_ids) or len(self.reviewer_labels) != len(
            self.reviewer_ids
        ):
            raise ContractError("INVALID_INPUT")
        if self.status == "DISPUTED":
            if self.final_label is not None:
                raise ContractError("INVALID_INPUT")
        elif self.status == "AGREED":
            if len(set(self.reviewer_labels)) != 1 or self.final_label != self.reviewer_labels[0]:
                raise ContractError("INVALID_INPUT")
        elif self.final_label is None or self.adjudicator_id is None:
            raise ContractError("INVALID_INPUT")
        return self


class BaselineSelection(Versioned):
    selection_digest: Digest
    pool_manifest_digest: Digest
    selected_dataset_digest: Digest
    selected_manifest_digest: Digest
    label_records_digest: Digest
    protocol_revision: Identifier
    selection_seed: Count
    case_ids: Annotated[tuple[Identifier, ...], Field(min_length=1, max_length=200)]
    family_ids: Annotated[tuple[Identifier, ...], Field(min_length=1, max_length=200)]
    split: Literal["calibration_200"]
    selection_before_predictions: Literal[True]


def validate_adjudications(dataset: LoadedDataset, records: tuple[Adjudication, ...]) -> None:
    indexed = {r.case_id: r for r in records}
    if len(indexed) != len(records) or set(indexed) != {c.case_id for c in dataset.cases}:
        raise ContractError("INVALID_INPUT")
    for case in dataset.cases:
        record = indexed[case.case_id]
        if (
            record.status == "DISPUTED"
            or record.final_label != case.reference_label
            or record.case_digest != digest(case)
            or case.reference_source.startswith("synthetic")
        ):
            raise ContractError("INTEGRITY_ERROR")


def read_adjudications(path: Path) -> tuple[Adjudication, ...]:
    return tuple(
        decode_model(Adjudication, line) for line in read_bounded(path, MAX_DATASET_BYTES).splitlines()
    )


def select_baseline(
    dataset: LoadedDataset,
    records: tuple[Adjudication, ...],
    *,
    seed: int = 44,
    size: int = 200,
    protocol_revision: str = "baseline-v1",
) -> BaselineSelection:
    verify_dataset(dataset)
    if (
        dataset.manifest.evidence_status != "HUMAN_ADJUDICATED"
        or type(size) is not int
        or not 1 <= size <= 200
        or type(seed) is not int
        or seed < 0
    ):
        raise ContractError("INVALID_INPUT")
    validate_adjudications(dataset, records)
    by_family: dict[str, Case] = {}
    for case in sorted(dataset.cases, key=lambda c: c.case_id):
        if case.split == "calibration_200":
            by_family.setdefault(case.case_family_id, case)
    if len(by_family) < size:
        raise ContractError("INVALID_INPUT")
    # Preserve legacy seeded sampling principle; sampling unit is now a frozen incident family.
    selected = sorted(random.Random(seed).sample(sorted(by_family), size))
    cases = tuple(sorted((by_family[f] for f in selected), key=lambda c: c.case_id))
    from judge_lab.load import dataset_digest

    metadata = dataset.manifest.model_dump(mode="json")
    metadata.update(
        sha256=dataset_digest(cases),
        split_algorithm="one case per family, frozen seeded selection",
        split_seed=seed,
    )
    chosen_ids = {c.case_id for c in cases}

    payload = {
        "schema_version": "1.0",
        "pool_manifest_digest": digest(dataset.manifest),
        "selected_dataset_digest": dataset_digest(cases),
        "selected_manifest_digest": digest(metadata),
        "label_records_digest": digest(
            [
                r.model_dump(mode="json")
                for r in sorted(records, key=lambda r: r.case_id)
                if r.case_id in chosen_ids
            ]
        ),
        "protocol_revision": protocol_revision,
        "selection_seed": seed,
        "case_ids": [c.case_id for c in cases],
        "family_ids": [c.case_family_id for c in cases],
        "split": "calibration_200",
        "selection_before_predictions": True,
    }
    return decode_model(BaselineSelection, canonical_bytes({**payload, "selection_digest": digest(payload)}))


def verify_selection(selection: BaselineSelection) -> None:
    if (
        selection.selection_digest != digest(selection.model_dump(mode="json", exclude={"selection_digest"}))
        or len(set(selection.case_ids)) != len(selection.case_ids)
        or len(set(selection.family_ids)) != len(selection.family_ids)
        or len(selection.case_ids) != len(selection.family_ids)
    ):
        raise ContractError("INTEGRITY_ERROR")


def evaluate_baseline(
    dataset: LoadedDataset,
    records: tuple[Adjudication, ...],
    selection: BaselineSelection,
    run: RunManifest,
    predictions: Path,
    reviewer_minutes: float,
) -> CalibrationReport:
    verify_selection(selection)
    validate_adjudications(dataset, records)
    if (
        len(dataset.cases) != 200
        or len(selection.case_ids) != 200
        or dataset.manifest.evidence_status != "HUMAN_ADJUDICATED"
        or dataset.manifest.sha256 != selection.selected_dataset_digest
        or digest(dataset.manifest) != selection.selected_manifest_digest
        or digest([r.model_dump(mode="json") for r in sorted(records, key=lambda r: r.case_id)])
        != selection.label_records_digest
        or set(selection.case_ids) != {c.case_id for c in dataset.cases}
        or set(selection.family_ids) != {c.case_family_id for c in dataset.cases}
        or any(c.split != "calibration_200" for c in dataset.cases)
        or not reviewer_minutes >= 0
        or not reviewer_minutes < float("inf")
    ):
        raise ContractError("INTEGRITY_ERROR")
    return build_report(dataset, import_predictions(predictions, dataset, run), run)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Frozen empirical baseline workflow; never fabricates labels"
    )
    parser.add_argument("action", choices=("select", "evaluate"))
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=44)
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--run-manifest", type=Path)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--reviewer-minutes", type=float)
    args = parser.parse_args(argv)
    try:
        dataset = load_dataset(args.data, args.manifest)
        records = read_adjudications(args.labels)
        if args.action == "select":
            selection = select_baseline(dataset, records, seed=args.seed)
            from judge_lab.load import dataset_jsonl

            chosen = tuple(c for c in dataset.cases if c.case_id in selection.case_ids)
            metadata = dataset.manifest.model_dump(mode="json")
            metadata.update(
                sha256=selection.selected_dataset_digest,
                split_algorithm="one case per family, frozen seeded selection",
                split_seed=args.seed,
            )
            write_bundle(
                args.out,
                {
                    "selection.json": canonical_bytes(selection),
                    "dataset.jsonl": dataset_jsonl(chosen),
                    "manifest.json": canonical_bytes(metadata),
                    "labels.jsonl": b"\n".join(
                        canonical_bytes(r) for r in records if r.case_id in selection.case_ids
                    ),
                },
            )
        else:
            if (not args.selection or not args.run_manifest or not args.predictions
                    or args.reviewer_minutes is None):
                raise ContractError("INVALID_INPUT")
            report = evaluate_baseline(
                dataset,
                records,
                read_config(BaselineSelection, args.selection),
                read_config(RunManifest, args.run_manifest),
                args.predictions,
                args.reviewer_minutes,
            )
            write_bundle(
                args.out,
                {
                    **report_files(report),
                    "review_cost.json": canonical_bytes(
                        {
                            "schema_version": "1.0",
                            "reviewer_minutes": args.reviewer_minutes,
                            "status": "USER_SUPPLIED",
                            "report_digest": report.report_digest,
                        }
                    ),
                },
            )
        return 0
    except (ContractError, OSError, ValueError):
        print(json.dumps({"status": "NOT_PERFORMED", "reason": "MISSING_OR_INVALID_EMPIRICAL_INPUTS"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
