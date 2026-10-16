import json
import time

import pytest

from judge_lab.artifacts import write_bundle
from judge_lab.contracts import ContractError, JudgeSpec
from judge_lab.provenance import build_run_manifest
from judge_lab.runner import (
    AdapterReply,
    DeterministicMockAdapter,
    import_predictions,
    parse_prediction,
    run_judge,
)
from judge_lab.serialization import canonical_bytes, decode_model


class SlowAdapter:
    version = "slow-v1"

    def evaluate(self, case, spec):
        time.sleep(30)
        return AdapterReply("ACCEPT")


class BadAdapter:
    version = "bad-v1"

    def evaluate(self, case, spec):
        return AdapterReply("ACCEPT because yes")


def make_run(dataset, spec, run, adapter):
    return build_run_manifest(dataset, spec, adapter_version=adapter.version, run_seed=run.run_seed,
                              environment=run.environment, created_at_utc=run.created_at_utc)


@pytest.mark.parametrize("text", ["", " ACCEPT", "ACCEPT\n", "accept", "ACCEPT because", "ERROR",
                                  '{"verdict":"ACCEPT"}', "\ud800", "ACCEPT\x00", "safe"])
def test_parser_contamination(text):
    with pytest.raises(ContractError, match="PARSE_ERROR"):
        parse_prediction(text)


def test_mock_import_repeatability_and_budgets(dataset, spec, run, tmp_path):
    adapter = DeterministicMockAdapter()
    run = make_run(dataset, spec, run, adapter)
    first = run_judge(dataset, spec, run)
    assert first == run_judge(dataset, spec, run)
    assert all(r.verdict in {"ACCEPT", "REJECT"} for r in first)
    output = tmp_path / "results.jsonl"
    output.write_bytes(b"\n".join(canonical_bytes(r) for r in reversed(first)))
    assert import_predictions(output, dataset, run) == first
    for bad in (first[:-1], (*first, first[0])):
        output.write_bytes(b"\n".join(canonical_bytes(r) for r in bad))
        with pytest.raises(ContractError):
            import_predictions(output, dataset, run)
    data = spec.model_dump(mode="json")
    data["limits"]["max_calls"] = 1
    limited = decode_model(JudgeSpec, json.dumps(data))
    limited_run = make_run(dataset, limited, run, adapter)
    results = run_judge(dataset, limited, limited_run)
    assert sum(r.error_kind == "BUDGET_EXCEEDED" for r in results) == 9
    assert all(r.verdict == "ERROR" for r in run_judge(dataset, spec, run, cancelled=lambda: True))


def test_timeout_and_parse_failure(dataset, spec, run):
    data = spec.model_dump(mode="json")
    data["limits"]["timeout_seconds"] = 0.1
    limited = decode_model(JudgeSpec, json.dumps(data))
    start = time.monotonic()
    results = run_judge(dataset, limited, make_run(dataset, limited, run, SlowAdapter()), SlowAdapter())
    assert results[0].error_kind == "TIMEOUT" and time.monotonic() - start < 5
    data["limits"].update(timeout_seconds=5, max_calls=1)
    limited = decode_model(JudgeSpec, json.dumps(data))
    results = run_judge(dataset, limited, make_run(dataset, limited, run, BadAdapter()), BadAdapter())
    assert results[0].error_kind == "PARSE_ERROR"


def test_atomic_bundle_ownership_and_paths(tmp_path):
    target = tmp_path / "run"
    write_bundle(target, {"result.json": b"{}"})
    with pytest.raises(ContractError):
        write_bundle(target, {"result.json": b"new"})
    assert (target / "result.json").read_bytes() == b"{}"
    write_bundle(target, {"result.json": b"new"}, overwrite=True)
    assert (target / "result.json").read_bytes() == b"new"
    with pytest.raises(ContractError):
        write_bundle(tmp_path / "../escape", {})
    with pytest.raises(ContractError):
        write_bundle(tmp_path / "other", {"../escape": b"bad"})
    other = tmp_path / "unowned"
    other.mkdir()
    with pytest.raises(ContractError):
        write_bundle(other, {}, overwrite=True)
    (tmp_path / "link").symlink_to(target)
    with pytest.raises(ContractError):
        write_bundle(tmp_path / "link", {}, overwrite=True)
