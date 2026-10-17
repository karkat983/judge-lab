"""Local CLI. Every failure message is a fixed code, never source/provider content."""

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

from judge_lab import __version__
from judge_lab.artifacts import write_bundle
from judge_lab.configuration import read_config
from judge_lab.contracts import ContractError, JudgeSpec, RunEnvironment, RunManifest
from judge_lab.load import load_dataset
from judge_lab.provenance import build_run_manifest, require_compatible_run
from judge_lab.reports import build_report, report_files
from judge_lab.runner import DeterministicMockAdapter, import_predictions, run_judge


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="judge-lab", description="Local scoped judge calibration")
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("validate", "calibrate"):
        command = sub.add_parser(name)
        command.add_argument("--data", type=Path, required=True)
        command.add_argument("--manifest", type=Path, required=True)
        command.add_argument("--judge", type=Path, required=True)
        if name == "calibrate":
            command.add_argument("--predictions", type=Path)
            command.add_argument("--run-manifest", type=Path)
            command.add_argument("--out", type=Path, required=True)
            command.add_argument("--overwrite", action="store_true")
            command.add_argument("--seed", type=int, default=44)
    demo = sub.add_parser("demo")
    demo.add_argument("--out", type=Path, default=Path("runs/demo"))
    demo.add_argument("--overwrite", action="store_true")
    probe = sub.add_parser("probe")
    for option in ("data", "dataset-manifest", "judge", "manifest", "out"):
        probe.add_argument("--" + option, type=Path, required=True)
    probe.add_argument("--vulnerable-mock", action="store_true")
    probe.add_argument("--predictions", type=Path)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "probe":
            from judge_lab.probes import command
            summary = command(args.data, args.dataset_manifest, args.judge, args.manifest,
                              args.out, args.vulnerable_mock, args.predictions)
            print(summary.model_dump_json())
            return 0
        if args.command == "demo":
            resource = files("judge_lab").joinpath("fixtures")
            args.data = Path(str(resource.joinpath("security_fixture.jsonl")))
            args.manifest = Path(str(resource.joinpath("security_manifest.json")))
            args.judge = Path(str(resource.joinpath("mock_judge.json")))
            args.predictions, args.run_manifest, args.seed = None, None, 44
        dataset = load_dataset(args.data, args.manifest)
        spec = read_config(JudgeSpec, args.judge)
        if any(c.rubric_revision != spec.rubric_revision for c in dataset.cases):
            raise ContractError("INTEGRITY_ERROR")
        if args.command == "validate":
            print(json.dumps(dataset.summary(), sort_keys=True))
            return 0
        if bool(args.predictions) != bool(args.run_manifest):
            raise ContractError("INVALID_INPUT")
        if args.predictions:
            run = read_config(RunManifest, args.run_manifest)
            expected = build_run_manifest(dataset, spec, adapter_version=run.adapter_version,
                run_seed=run.run_seed, environment=run.environment, created_at_utc=run.created_at_utc)
            require_compatible_run(run, expected)
            results = import_predictions(args.predictions, dataset, run)
        else:
            if spec.adapter != "deterministic_mock":
                raise ContractError("INVALID_INPUT")
            run = build_run_manifest(dataset, spec, adapter_version=DeterministicMockAdapter.version,
                run_seed=args.seed, environment=RunEnvironment(python=platform.python_version(),
                platform=platform.system(), package_version=__version__), created_at_utc=datetime.now(UTC))
            results = run_judge(dataset, spec, run)
        report = build_report(dataset, results, run)
        write_bundle(args.out, report_files(report), overwrite=args.overwrite)
        print("synthetic demonstration, not product effectiveness evidence" if
              dataset.manifest.evidence_status == "SYNTHETIC" else "scoped reliability evaluation")
        print(json.dumps({"report_digest": report.report_digest, "output": str(args.out)}, sort_keys=True))
        return 0
    except (ContractError, OSError, ValueError):
        print("INVALID_INPUT_OR_INTEGRITY_ERROR", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
