import json

import pytest

from judge_lab.baseline import (
    Adjudication,
    select_baseline,
    validate_adjudications,
    verify_selection,
)
from judge_lab.contracts import Case, ContractError, DatasetRevision
from judge_lab.load import LoadedDataset, dataset_digest
from judge_lab.metrics import binary_statistics
from judge_lab.serialization import canonical_bytes, decode_model, digest


def controlled_human_shaped_input(dataset):
    # Synthetic unit test of declarations only; never persisted or called empirical evidence.
    cases = tuple(
        decode_model(
            Case,
            canonical_bytes(
                {
                    **c.model_dump(mode="json"),
                    "split": "calibration_200",
                    "reference_source": "human-declaration",
                }
            ),
        )
        for c in dataset.cases
    )
    manifest = decode_model(
        DatasetRevision,
        canonical_bytes(
            {
                **dataset.manifest.model_dump(mode="json"),
                "evidence_status": "HUMAN_ADJUDICATED",
                "sha256": dataset_digest(cases),
            }
        ),
    )
    records = tuple(
        Adjudication(
            schema_version="1.0",
            case_id=c.case_id,
            case_digest=digest(c),
            reviewer_ids=("reviewer-1", "reviewer-2"),
            reviewer_labels=(c.reference_label, c.reference_label),
            status="AGREED",
            final_label=c.reference_label,
            adjudicator_id=None,
            independent_of_judge=True,
            frozen=True,
            source="HUMAN",
        )
        for c in cases
    )
    return LoadedDataset(manifest, cases), records


def test_selection_is_seeded_frozen_and_rejects_synthetic_or_insufficient(dataset):
    with pytest.raises(ContractError):
        select_baseline(dataset, (), size=1)
    declared, records = controlled_human_shaped_input(dataset)
    first = select_baseline(declared, records, size=5)
    assert first == select_baseline(declared, tuple(reversed(records)), size=5)
    verify_selection(first)
    assert len(set(first.family_ids)) == 5
    assert first != select_baseline(declared, records, seed=45, size=5)
    with pytest.raises(ContractError):
        select_baseline(declared, records)
    with pytest.raises(ContractError):
        validate_adjudications(declared, records[:-1])
    bad = first.model_dump(mode="json")
    bad["selection_seed"] = 999
    with pytest.raises(ContractError):
        verify_selection(decode_model(type(first), json.dumps(bad)))


def test_disagreement_not_automatic_truth_and_holdout_not_sampled(dataset):
    declared, records = controlled_human_shaped_input(dataset)
    disputed = decode_model(
        Adjudication,
        canonical_bytes({**records[0].model_dump(mode="json"), "status": "DISPUTED", "final_label": None}),
    )
    with pytest.raises(ContractError):
        validate_adjudications(declared, (disputed, *records[1:]))
    cases = tuple(
        decode_model(Case, canonical_bytes({**c.model_dump(mode="json"), "split": "heldout_test"}))
        for c in declared.cases
    )
    manifest = decode_model(
        DatasetRevision,
        canonical_bytes({**declared.manifest.model_dump(mode="json"), "sha256": dataset_digest(cases)}),
    )
    refreshed = tuple(
        decode_model(Adjudication, canonical_bytes({**r.model_dump(mode="json"), "case_digest": digest(c)}))
        for r, c in zip(records, cases, strict=True)
    )
    with pytest.raises(ContractError):
        select_baseline(LoadedDataset(manifest, cases), refreshed, size=1)


def test_simple_baseline_loop_matches_core():
    references = ("ACCEPT", "REJECT", "REJECT", "ACCEPT", "REJECT")
    predictions = ("REJECT", "ACCEPT", "REJECT", "ABSTAIN", "ERROR")
    correct = sum(r == p for r, p in zip(references, predictions, strict=True))
    answers = sum(p in ("ACCEPT", "REJECT") for p in predictions)
    false_accepts = sum(r == "REJECT" and p == "ACCEPT" for r, p in zip(references, predictions, strict=True))
    stats = binary_statistics(references, predictions)
    assert stats.metrics["conditional_accuracy"].value == correct / answers
    assert stats.counts["RA"] == false_accepts


def test_complete_200_pipeline_on_explicit_test_data(dataset, spec, run, tmp_path):
    from judge_lab.baseline import evaluate_baseline
    from judge_lab.provenance import build_run_manifest
    from judge_lab.runner import DeterministicMockAdapter, run_judge

    # 200 manufactured test records validate software ONLY. Never exported as empirical evidence.
    cases = tuple(
        decode_model(
            Case,
            canonical_bytes(
                {
                    **dataset.cases[i % 10].model_dump(mode="json"),
                    "case_id": f"test-{i}",
                    "case_family_id": f"test-family-{i}",
                    "split": "calibration_200",
                    "reference_source": "test-human-declaration",
                }
            ),
        )
        for i in range(200)
    )
    metadata = {
        **dataset.manifest.model_dump(mode="json"),
        "sha256": dataset_digest(cases),
        "evidence_status": "HUMAN_ADJUDICATED",
    }
    pool = LoadedDataset(decode_model(DatasetRevision, canonical_bytes(metadata)), cases)
    records = tuple(
        Adjudication(
            schema_version="1.0",
            case_id=c.case_id,
            case_digest=digest(c),
            reviewer_ids=("test-1", "test-2"),
            reviewer_labels=(c.reference_label, c.reference_label),
            status="AGREED",
            final_label=c.reference_label,
            adjudicator_id=None,
            independent_of_judge=True,
            frozen=True,
            source="HUMAN",
        )
        for c in cases
    )
    selection = select_baseline(pool, records)
    metadata.update(split_algorithm="one case per family, frozen seeded selection", split_seed=44)
    selected = LoadedDataset(decode_model(DatasetRevision, canonical_bytes(metadata)), cases)
    bound = build_run_manifest(
        selected,
        spec,
        adapter_version=DeterministicMockAdapter.version,
        run_seed=44,
        environment=run.environment,
        created_at_utc=run.created_at_utc,
    )
    results = run_judge(selected, spec, bound)
    path = tmp_path / "test-predictions.jsonl"
    path.write_bytes(b"\n".join(canonical_bytes(r) for r in results))
    report = evaluate_baseline(selected, records, selection, bound, path, 0)
    assert report.statistics.denominators["eligible_total"] == 200
    changed = decode_model(
        Adjudication,
        canonical_bytes({**records[0].model_dump(mode="json"), "reviewer_ids": ["other-1", "other-2"]}),
    )
    with pytest.raises(ContractError):
        evaluate_baseline(selected, (changed, *records[1:]), selection, bound, path, 0)
