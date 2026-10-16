import json
import traceback

import pytest
from pydantic import ValidationError

from judge_lab.contracts import Case, ContractError, DatasetRevision, JudgeResult, JudgeSpec, RunManifest
from judge_lab.serialization import canonical_bytes, decode_model


def case_from(data):
    return decode_model(Case, json.dumps(data))


def test_fixture_contracts_and_outcomes(dataset, spec, run):
    from pathlib import Path

    from judge_lab.provenance import verify_result, verify_run_manifest

    assert len(dataset.cases) == 10
    assert dataset.manifest.evidence_status == "SYNTHETIC"
    assert {c.reference_source for c in dataset.cases} == {"synthetic-planted-rule"}
    assert {c.split for c in dataset.cases} == {"development"}
    assert sum(c.reference_label == "REJECT" for c in dataset.cases) == 5
    assert {reason for c in dataset.cases for reason in c.reference_reason_codes} == {
        "FABRICATED_EVIDENCE", "PROHIBITED_ACTION", "UNSUPPORTED_RCA", "MISSING_REQUIRED_EVIDENCE",
    }
    for model in (dataset.manifest, spec, run, *dataset.cases):
        assert decode_model(type(model), canonical_bytes(model)) == model
    verify_run_manifest(run)
    path = Path(__file__).resolve().parents[2] / "examples" / "synthetic_results.jsonl"
    results = [decode_model(JudgeResult, line) for line in path.read_bytes().splitlines()]
    for case, result in zip(dataset.cases, results, strict=True):
        verify_result(result, case, run, dataset)
    assert results[-2].verdict == "ABSTAIN" and results[-2].error_kind is None
    assert results[-1].verdict == "ERROR" and results[-1].error_kind == "PARSE_ERROR"
    assert all(result.raw_output_ref is None for result in results)


@pytest.mark.parametrize(("field", "value"), [
    ("schema_version", "2.0"), ("schema_version", 1), ("case_id", ""), ("case_id", "../escape"),
    ("case_id", 123), ("case_family_id", ""), ("report_text", ""), ("report_text", "  "),
    ("report_text", "x" * 32769), ("report_text", "\x00"), ("report_text", "\ud800"),
    ("reference_label", "safe"), ("reference_label", "unsafe"), ("reference_label", "ABSTAIN"),
    ("reference_label", "ERROR"), ("reference_label", "DISPUTED"), ("reference_label", None),
    ("reference_frozen", False), ("reference_frozen", "true"), ("reference_frozen", 1),
    ("split", "unknown"), ("reference_reason_codes", [123]), ("authoritative_evidence", []),
])
def test_invalid_case_fields_rejected(case_data, field, value):
    case_data[field] = value
    with pytest.raises(ContractError, match="INVALID_INPUT"):
        case_from(case_data)


@pytest.mark.parametrize("field", ["schema_version", "case_id", "case_family_id", "reference_label"])
def test_required_fields_never_inferred(case_data, field):
    del case_data[field]
    with pytest.raises(ContractError):
        case_from(case_data)


def test_unknown_keys_duplicate_evidence_policy_conflicts(case_data):
    for change in (
        {"decision": "PASS"},
        {"authoritative_evidence": case_data["authoritative_evidence"] * 2},
        {"policy_constraints": {"allowed_actions": ["restart"], "prohibited_actions": ["restart"]}},
        {"reference_label": "REJECT", "reference_reason_codes": []},
    ):
        with pytest.raises(ContractError):
            case_from({**case_data, **change})


def test_deep_immutability(case_data):
    case = case_from(case_data)
    for name, value in (("split", "heldout_test"), ("case_family_id", "changed")):
        with pytest.raises(ValidationError):
            setattr(case, name, value)
    with pytest.raises(ValidationError):
        case.authoritative_evidence[0].text = "changed"
    with pytest.raises(TypeError):
        case.reference_reason_codes[0] = "changed"
    case_data["authoritative_evidence"][0]["text"] = "changed outside"
    assert case.authoritative_evidence[0].text != "changed outside"


@pytest.mark.parametrize(("verdict", "error"), [
    ("ERROR", None), ("ACCEPT", "TIMEOUT"), ("ABSTAIN", "PROVIDER_ERROR"),
    ("ERROR", "unknown"), ("safe", None), ("PASS", None), ("ACCEPT because good", None),
    ('{"verdict":"ACCEPT"}', None), (" accept ", None),
])
def test_result_outcomes_do_not_hide_failures(result_data, verdict, error):
    result_data.update(verdict=verdict, error_kind=error)
    with pytest.raises(ContractError):
        decode_model(JudgeResult, json.dumps(result_data))


@pytest.mark.parametrize("error", ["INVALID_INPUT", "PARSE_ERROR", "TIMEOUT", "PROVIDER_ERROR",
                                  "BUDGET_EXCEEDED"])
def test_explicit_execution_errors(result_data, error):
    result_data.update(verdict="ERROR", error_kind=error, estimated_cost_usd=None)
    result = decode_model(JudgeResult, json.dumps(result_data))
    assert result.verdict == "ERROR" and result.error_kind == error
    assert result.estimated_cost_usd is None


@pytest.mark.parametrize(("field", "value"), [
    ("input_tokens", -1), ("input_tokens", True), ("input_tokens", "10"),
    ("output_tokens", 1.2), ("latency_ms", -0.1), ("estimated_cost_usd", -1),
    ("estimated_cost_usd", float("nan")), ("latency_ms", float("inf")),
    ("judge_spec_digest", "sha256:short"), ("run_id", "old-run"),
    ("raw_output_ref", "raw-confidential-response"),
])
def test_result_strict_numbers_and_provenance(result_data, field, value):
    result_data[field] = value
    with pytest.raises(ContractError):
        decode_model(JudgeResult, json.dumps(result_data))


def test_judge_spec_rejects_live_adapter_and_invalid_limits(spec):
    data = spec.model_dump(mode="json")
    for change in ({"adapter": "anthropic"}, {"parser": "fallback"},
                   {"limits": {**data["limits"], "max_calls": 0}},
                   {"limits": {**data["limits"], "timeout_seconds": -1}},
                   {"settings": {**data["settings"], "temperature": "0"}}):
        with pytest.raises(ContractError):
            decode_model(JudgeSpec, json.dumps({**data, **change}))


@pytest.mark.parametrize("timestamp", ["2026-10-17", "2026-10-17T00:00:00", "not-a-date",
                                       "2026-10-17T00:00:00+05:30", 1])
def test_utc_required(dataset, timestamp):
    data = dataset.manifest.model_dump(mode="json")
    data["created_at_utc"] = timestamp
    with pytest.raises(ContractError):
        decode_model(DatasetRevision, json.dumps(data))


@pytest.mark.parametrize("model", [Case, DatasetRevision, JudgeSpec, JudgeResult, RunManifest])
def test_all_external_models_reject_unsupported_version(model):
    with pytest.raises(ContractError):
        decode_model(model, '{"schema_version":"9.0"}')


def test_validation_errors_and_reprs_do_not_echo_secrets(case_data, capsys, caplog):
    canary = "CONFIDENTIAL-CANARY-123"
    case_data["report_text"] = canary
    valid = case_from(case_data)
    assert canary not in repr(valid) and canary not in str(valid)
    for data in ({**case_data, canary: "extra"}, {**case_data, "reference_label": canary}):
        try:
            case_from(data)
        except ContractError as exc:
            assert canary not in str(exc)
            assert canary not in repr(exc)
            assert canary not in "".join(traceback.format_exception(exc))
        else:
            pytest.fail("invalid secret-bearing payload accepted")
    assert not capsys.readouterr().out and not caplog.text
