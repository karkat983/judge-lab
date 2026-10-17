import html
import json
from pathlib import Path

import pytest

from judge_lab.cli import main
from judge_lab.configuration import read_config
from judge_lab.contracts import ContractError, JudgeSpec
from judge_lab.reports import CalibrationReport, build_report, render_html, verify_report
from judge_lab.runner import import_predictions
from judge_lab.serialization import canonical_bytes, decode_model, digest

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def test_cli_demo_installed_resources_output_and_collision(tmp_path, capsys):
    out = tmp_path / "demo"
    assert main(["demo", "--out", str(out)]) == 0
    assert "not product effectiveness evidence" in capsys.readouterr().out
    report = decode_model(CalibrationReport, (out / "report.json").read_bytes())
    verify_report(report)
    assert report.statistics.metrics["coverage"].value == 1
    body = (out / "report.html").read_text().split("<pre>")[1].split("</pre>")[0]
    assert json.loads(html.unescape(body)) == report.model_dump(mode="json")
    before = (out / "report.json").read_bytes()
    assert main(["demo", "--out", str(out)]) == 2
    assert (out / "report.json").read_bytes() == before
    assert main(["demo", "--out", str(out), "--overwrite"]) == 0


def test_validate_and_imported_predictions_cli(tmp_path, capsys):
    args = [
        "--data",
        str(EXAMPLES / "security_fixture.jsonl"),
        "--manifest",
        str(EXAMPLES / "security_manifest.json"),
        "--judge",
        str(EXAMPLES / "mock_judge.json"),
    ]
    assert main(["validate", *args]) == 0
    assert json.loads(capsys.readouterr().out)["case_count"] == 10
    out = tmp_path / "imported"
    assert (
        main(
            [
                "calibrate",
                *args,
                "--out",
                str(out),
                "--predictions",
                str(EXAMPLES / "synthetic_results.jsonl"),
                "--run-manifest",
                str(EXAMPLES / "synthetic_run.json"),
            ]
        )
        == 0
    )
    report = decode_model(CalibrationReport, (out / "report.json").read_bytes())
    assert report.statistics.metrics["coverage"].value == 0.8
    assert (
        main(
            [
                "calibrate",
                *args,
                "--out",
                str(tmp_path / "bad"),
                "--predictions",
                str(EXAMPLES / "synthetic_results.jsonl"),
            ]
        )
        == 2
    )


def test_malicious_html_escaped_and_tamper_rejected(dataset, run):
    results = import_predictions(EXAMPLES / "synthetic_results.jsonl", dataset, run)
    report = build_report(dataset, results, run)
    payload = report.model_dump(mode="json", exclude={"report_digest"})
    payload["limitations"] = ['<script>alert("bad")</script>']
    altered = decode_model(CalibrationReport, canonical_bytes({**payload, "report_digest": digest(payload)}))
    page = render_html(altered).decode()
    assert "<script>" not in page and "&lt;script&gt;" in page
    payload["statistics"]["metrics"]["coverage"]["value"] = 1
    tampered = decode_model(CalibrationReport, canonical_bytes({**payload, "report_digest": digest(payload)}))
    with pytest.raises(ContractError):
        verify_report(tampered)


def test_private_report_text_and_source_never_exported(dataset, run, spec):
    from judge_lab.contracts import Case, DatasetRevision
    from judge_lab.load import LoadedDataset, dataset_digest
    from judge_lab.provenance import build_run_manifest
    from judge_lab.runner import DeterministicMockAdapter, run_judge

    canary = "PRIVATE-CANARY-123"
    changed = dataset.cases[0].model_dump(mode="json")
    changed["report_text"] = canary
    cases = (decode_model(Case, canonical_bytes(changed)), *dataset.cases[1:])
    metadata = {**dataset.manifest.model_dump(mode="json"), "source": canary, "sha256": dataset_digest(cases)}
    dataset = LoadedDataset(decode_model(DatasetRevision, canonical_bytes(metadata)), cases)
    run = build_run_manifest(
        dataset,
        spec,
        adapter_version=DeterministicMockAdapter.version,
        run_seed=44,
        environment=run.environment,
        created_at_utc=run.created_at_utc,
    )
    report = build_report(dataset, run_judge(dataset, spec, run), run)
    assert canary.encode() not in canonical_bytes(report)
    assert canary.encode() not in render_html(report)


@pytest.mark.parametrize(
    "text", ["x: 1\nx: 2", "a: &a [x]\nb: *a", "!!python/object/apply:os.system ['bad']"]
)
def test_yaml_rejects_duplicates_aliases_and_tags(tmp_path, text):
    path = tmp_path / "bad.yaml"
    path.write_text(text)
    with pytest.raises(ContractError):
        read_config(JudgeSpec, path)


def test_yaml_and_packaged_fixtures_match(tmp_path, spec):
    import yaml

    path = tmp_path / "judge.yaml"
    path.write_text(yaml.safe_dump(spec.model_dump(mode="json")))
    assert read_config(JudgeSpec, path) == spec
    root = EXAMPLES.parent / "src" / "judge_lab" / "fixtures"
    for name in ("security_fixture.jsonl", "security_manifest.json", "mock_judge.json"):
        assert (root / name).read_bytes() == (EXAMPLES / name).read_bytes()


def test_cli_private_failure(tmp_path, capsys):
    args = [
        "validate",
        "--data",
        str(tmp_path / "PRIVATE-secret"),
        "--manifest",
        "absent",
        "--judge",
        "absent",
    ]
    assert main(args) == 2
    captured = capsys.readouterr()
    assert "PRIVATE" not in captured.err and "Traceback" not in captured.err
