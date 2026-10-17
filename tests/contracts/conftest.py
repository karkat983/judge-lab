import json
import socket
from pathlib import Path

import pytest

from judge_lab.contracts import JudgeSpec, RunManifest
from judge_lab.load import load_dataset
from judge_lab.serialization import decode_model

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Phase 01 must be offline")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)


@pytest.fixture
def dataset():
    return load_dataset(EXAMPLES / "security_fixture.jsonl", EXAMPLES / "security_manifest.json")


@pytest.fixture
def case_data():
    return json.loads((EXAMPLES / "security_fixture.jsonl").read_text(encoding="utf-8").splitlines()[0])


@pytest.fixture
def spec():
    return decode_model(JudgeSpec, (EXAMPLES / "mock_judge.json").read_bytes())


@pytest.fixture
def run():
    return decode_model(RunManifest, (EXAMPLES / "synthetic_run.json").read_bytes())


@pytest.fixture
def result_data():
    return json.loads((EXAMPLES / "synthetic_results.jsonl").read_text(encoding="utf-8").splitlines()[0])


@pytest.fixture
def report_factory(dataset, spec, run):
    """Manufactured test records ONLY; human-shaped status is never empirical evidence."""
    from judge_lab.contracts import Case, DatasetRevision, JudgeSpec
    from judge_lab.load import LoadedDataset, dataset_digest
    from judge_lab.provenance import build_run_manifest
    from judge_lab.reports import build_report
    from judge_lab.runner import AdapterReply, bind_result
    from judge_lab.serialization import canonical_bytes

    def make(n=100, split="heldout_test", evidence="SYNTHETIC", predictions=None):
        cases = tuple(
            decode_model(
                Case,
                canonical_bytes(
                    {
                        **dataset.cases[i % 10].model_dump(mode="json"),
                        "case_id": f"test-{split}-{i}",
                        "case_family_id": f"test-{split}-family-{i}",
                        "split": split,
                    }
                ),
            )
            for i in range(n)
        )
        metadata = decode_model(
            DatasetRevision,
            canonical_bytes(
                {
                    **dataset.manifest.model_dump(mode="json"),
                    "sha256": dataset_digest(cases),
                    "evidence_status": evidence,
                }
            ),
        )
        data = LoadedDataset(metadata, cases)
        judge = decode_model(
            JudgeSpec,
            canonical_bytes(
                {
                    **spec.model_dump(mode="json"),
                    "limits": {**spec.limits.model_dump(mode="json"), "max_calls": 1000},
                }
            ),
        )
        bound = build_run_manifest(
            data,
            judge,
            adapter_version="mock-rules-v1",
            run_seed=44,
            environment=run.environment,
            created_at_utc=run.created_at_utc,
        )
        results = tuple(
            bind_result(c, bound, AdapterReply(predictions[i] if predictions else c.reference_label))
            for i, c in enumerate(cases)
        )
        return build_report(data, results, bound)

    return make
