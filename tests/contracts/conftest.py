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
