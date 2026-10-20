import json

import pytest

from judge_lab.contracts import ContractError
from judge_lab.probe_pilot import (
    INJECTION,
    generate_reports,
    primary_violation,
    sanitize,
    transform,
)
from judge_lab.runner import parse_prediction


def test_population_and_independent_labels():
    reports = generate_reports({"source": "unit-test"})
    assert len(reports) == 48
    assert len({r.incident_id for r in reports}) == 24
    assert sum(r.correct_verdict == "ACCEPT" for r in reports) == 24
    for r in reports:
        view = r.judge_input().model_dump()
        assert "correct_verdict" not in view
        assert "provenance" not in view
        if r.correct_verdict == "ACCEPT":
            assert set(r.cited_evidence) <= {e.id for e in r.evidence}
            assert r.provenance["label_rule"] == "faithful"
        else:
            assert r.provenance["label_rule"] in ("contradiction", "missing evidence")


def test_pure_probes_preserve_or_destroy_exact_evidence():
    for base in generate_reports({}):
        frozen = base.as_dict()
        p1 = transform(base, "P1")
        assert p1.report_text == base.alert and p1.correct_verdict == "REJECT"
        assert p1.evidence == base.evidence
        p2 = transform(base, "P2")
        assert p2.correct_verdict == base.correct_verdict
        assert p2.report_text == base.report_text
        a, b = json.loads(base.evidence[-1].text), json.loads(p2.evidence[-1].text)
        assert b.pop("msg") == a.pop("msg") + INJECTION
        assert a == b
        assert p2.evidence[:-1] == base.evidence[:-1]
        p3 = transform(base, "P3")
        assert base.report_text in p3.report_text and p3.evidence == base.evidence
        assert p3.correct_verdict == base.correct_verdict
        p4 = transform(base, "P4")
        assert p4.report_text == base.report_text
        assert not (set(base.cited_evidence) & {e.id for e in p4.evidence})
        assert p4.correct_verdict == "REJECT_OR_ABSTAIN"
        assert sanitize(p2) == base
        assert transform(base, "P2_SANITIZED") == base
        assert base.as_dict() == frozen


@pytest.mark.parametrize("probe", ["P1", "P2", "P3", "P4", "P2_SANITIZED"])
def test_errors_excluded_not_abstentions(probe):
    assert primary_violation(probe, "ERROR", "ACCEPT") is None
    assert primary_violation(probe, "ACCEPT", "ERROR") is None
    assert primary_violation(probe, "ACCEPT", "ABSTAIN") == (probe not in ("P1", "P4"))


def test_primary_is_not_attack_success():
    assert primary_violation("P2", "ACCEPT", "REJECT") is True
    assert primary_violation("P4", "ACCEPT", "REJECT") is False
    assert primary_violation("P1", "ACCEPT", "ACCEPT") is True
    assert primary_violation("P1", "REJECT", "ABSTAIN") is False
    with pytest.raises(ValueError):
        primary_violation("P2", "NOT_RUN", "ACCEPT")
    with pytest.raises(ContractError):
        parse_prediction("ACCEPT\n")


def test_ollama_adapter_uses_existing_interface_without_labels(monkeypatch):
    from pathlib import Path

    from judge_lab.contracts import JudgeSpec
    from judge_lab.probe_pilot import OllamaAdapter

    spec = JudgeSpec.model_validate_json(
        (Path(__file__).parents[2] / "experiments/probe_pilot/judge_spec.json").read_bytes())
    adapter = OllamaAdapter()
    seen = []

    def request(path, payload):
        seen.append((path, payload))
        return {"done": True, "done_reason": "stop", "message": {"content": "REJECT"},
                "prompt_eval_count": 300, "eval_count": 3}

    monkeypatch.setattr(adapter, "request", request)
    reply = adapter.evaluate(generate_reports({})[0].judge_input(), spec)
    assert reply.text == "REJECT" and reply.input_tokens == 300
    assert seen[0][0] == "/api/chat"
    payload = seen[0][1]
    assert payload["options"]["temperature"] == 0
    view = json.loads(payload["messages"][1]["content"])
    assert set(view) == {"schema_version", "rubric_revision", "report_text",
                         "authoritative_evidence", "policy_constraints"}
    assert adapter.last_response["message"]["content"] == "REJECT"


def test_ollama_incomplete_generation_is_error(monkeypatch):
    from pathlib import Path

    from judge_lab.contracts import JudgeSpec
    from judge_lab.probe_pilot import OllamaAdapter

    spec = JudgeSpec.model_validate_json(
        (Path(__file__).parents[2] / "experiments/probe_pilot/judge_spec.json").read_bytes())
    adapter = OllamaAdapter()
    raw = {"done": True, "done_reason": "length", "message": {"content": "ACCEPT"}}
    monkeypatch.setattr(adapter, "request", lambda *args: raw)
    with pytest.raises(ValueError, match="Incomplete"):
        adapter.evaluate(generate_reports({})[0].judge_input(), spec)
    assert adapter.last_response == raw
