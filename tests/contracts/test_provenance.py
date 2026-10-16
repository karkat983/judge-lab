import hashlib
import json
from datetime import timedelta

import pytest

from judge_lab.contracts import Case, ContractError, DatasetRevision, JudgeResult, JudgeSpec
from judge_lab.load import LoadedDataset, dataset_digest
from judge_lab.provenance import (
    build_run_manifest,
    require_compatible_run,
    verify_result,
    verify_run_manifest,
)
from judge_lab.serialization import canonical_bytes, decode_model, digest


def updated(model, **changes):
    return decode_model(type(model), json.dumps({**model.model_dump(mode="json"), **changes}))


def build(dataset, spec, run, **changes):
    kwargs = {"adapter_version": run.adapter_version, "run_seed": run.run_seed,
              "environment": run.environment, "created_at_utc": run.created_at_utc}
    return build_run_manifest(dataset, spec, **{**kwargs, **changes})


def test_independent_canonical_golden_and_newline_equivalence():
    expected = b'{"a":[1,true,null],"z":"caf\xc3\xa9\\nline"}'
    value = {"z": "café\r\nline", "a": [1, True, None]}
    assert canonical_bytes(value) == expected
    assert digest(value) == "sha256:" + hashlib.sha256(expected).hexdigest()
    assert digest(value) == digest({"a": [1, True, None], "z": "café\nline"})
    assert digest([1, 2]) != digest([2, 1])
    assert digest("1") != digest(1)


def test_run_identity_reproducible_and_time_is_not_compatibility(dataset, spec, run):
    reconstructed = build(dataset, spec, run)
    assert reconstructed == run
    later = build(dataset, spec, run, created_at_utc=run.created_at_utc + timedelta(days=1))
    require_compatible_run(run, later)
    assert later.run_id == run.run_id


@pytest.mark.parametrize("field", ["report_text", "reference_label", "split", "case_family_id",
                                  "authoritative_evidence", "policy_constraints"])
def test_case_changes_invalidate_existing_run(dataset, spec, run, field):
    data = dataset.cases[0].model_dump(mode="json")
    changes = {
        "report_text": data["report_text"] + " changed",
        "reference_label": "REJECT", "split": "heldout_test", "case_family_id": "changed-family",
        "authoritative_evidence": [{"id": "new-log", "type": "log", "text": "changed"}],
        "policy_constraints": {"allowed_actions": ["read_logs"], "prohibited_actions": []},
    }
    data[field] = changes[field]
    if field == "reference_label":
        data["reference_reason_codes"] = ["NEW-REASON"]
    changed = decode_model(Case, json.dumps(data))
    cases = (changed, *dataset.cases[1:])
    manifest = updated(dataset.manifest, sha256=dataset_digest(cases))
    candidate = build(LoadedDataset(manifest, cases), spec, run)
    assert candidate.run_id != run.run_id
    with pytest.raises(ContractError, match="INTEGRITY_ERROR"):
        require_compatible_run(run, candidate)


@pytest.mark.parametrize("change", ["rubric", "model", "settings", "budget", "adapter", "seed",
                                   "environment", "label_protocol", "license", "revision"])
def test_configuration_changes_invalidate_run(dataset, spec, run, change):
    data = spec.model_dump(mode="json")
    overrides = {}
    if change == "rubric":
        data["rubric_text"] += " Changed policy."
    elif change == "model":
        data["model_ref"] = "mock:other"
    elif change == "settings":
        data["settings"]["temperature"] = 0.5
    elif change == "budget":
        data["limits"]["max_calls"] += 1
    elif change == "adapter":
        overrides["adapter_version"] = "fixture-v2"
    elif change == "seed":
        overrides["run_seed"] = 45
    elif change == "environment":
        overrides["environment"] = updated(run.environment, package_version="0.2.0")
    else:
        field = {"label_protocol": "label_protocol_revision", "license": "license_or_permission",
                 "revision": "dataset_revision"}[change]
        manifest = updated(dataset.manifest, **{field: "changed"})
        dataset = LoadedDataset(manifest, dataset.cases)
    candidate = build(dataset, decode_model(JudgeSpec, json.dumps(data)), run, **overrides)
    with pytest.raises(ContractError):
        require_compatible_run(run, candidate)


def test_stale_metadata_and_tampered_run_rejected(dataset, spec, run):
    changed = updated(dataset.cases[0], report_text="changed")
    with pytest.raises(ContractError):
        build(LoadedDataset(dataset.manifest, (changed, *dataset.cases[1:])), spec, run)
    with pytest.raises(ContractError):
        verify_run_manifest(updated(run, adapter_version="tampered"))
    with pytest.raises(ContractError):
        build(dataset, updated(spec, rubric_revision="other"), run)


@pytest.mark.parametrize(("field", "value"), [
    ("case_id", "wrong-case"), ("case_digest", "sha256:" + "0" * 64),
    ("run_id", "sha256:" + "0" * 64), ("judge_spec_digest", "sha256:" + "0" * 64),
])
def test_result_binding_rejects_stale_or_wrong_case(dataset, run, result_data, field, value):
    result = decode_model(JudgeResult, json.dumps({**result_data, field: value}))
    with pytest.raises(ContractError):
        verify_result(result, dataset.cases[0], run, dataset)


def test_result_cannot_use_different_dataset_manifest(dataset, run, result_data):
    result = decode_model(JudgeResult, json.dumps(result_data))
    manifest = updated(dataset.manifest, dataset_revision="other")
    assert isinstance(manifest, DatasetRevision)
    with pytest.raises(ContractError):
        verify_result(result, dataset.cases[0], run, LoadedDataset(manifest, dataset.cases))
