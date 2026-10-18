#!/usr/bin/env python3
"""Three explicit, bounded Ollama stages for preregistered pilot 2."""

import argparse
import hashlib
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from judge_lab.contracts import ContractError, JudgeSpec
from judge_lab.probe_pilot import OllamaAdapter
from judge_lab.probe_pilot_2 import MODEL_DIGEST, PROBES, generate_reports_2, transform_2
from judge_lab.runner import parse_prediction

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/probe_pilot_2"
RUN = ROOT / "runs/probe-pilot-2/llama3.1-8b"
FROZEN = ["experiments/probe_pilot_2/PREREG.md", "experiments/probe_pilot_2/base_reports.jsonl",
          "experiments/probe_pilot_2/source_provenance.json", "experiments/probe_pilot_2/judge_spec.json",
          "src/judge_lab/probe_pilot.py", "src/judge_lab/probe_pilot_2.py",
          "scripts/run_probe_pilot_2.py", "scripts/report_probe_pilot_2.py"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read(path):
    return json.loads(path.read_text())


def reports():
    data = generate_reports_2(read(EXP / "source_provenance.json"))
    serialized = "".join(json.dumps(r.as_dict(), sort_keys=True) + "\n" for r in data)
    if serialized != (EXP / "base_reports.jsonl").read_text():
        raise RuntimeError("Dataset differs from frozen generator")
    return data


def require_committed(path):
    relative = str(path.relative_to(ROOT))
    if not git("ls-files", "--", relative):
        raise RuntimeError(f"Missing committed evidence: {relative}")
    if git("status", "--porcelain", "--untracked-files=all", "--", relative):
        raise RuntimeError(f"Uncommitted evidence: {relative}")


def run(stage):
    for relative in FROZEN:
        require_committed(ROOT / relative)
    prior_elapsed = 0
    selected = None
    if stage in ("probes", "sanitizer"):
        require_committed(RUN / "base")
        require_committed(EXP / "base_check.md")
        prior_elapsed += read(RUN / "base/completion.json")["elapsed_seconds"]
    if stage == "sanitizer":
        require_committed(RUN / "probes")
        require_committed(EXP / "sanitizer_selection.json")
        prior_elapsed += read(RUN / "probes/completion.json")["elapsed_seconds"]
        selected = read(EXP / "sanitizer_selection.json")["selected"]
        # Recompute the preregistered rule; refuse a hand-edited selection.
        from report_probe_pilot_2 import selection
        assert selection()["selected"] == selected
    conditions = {"base": ("BASE",), "probes": PROBES, "sanitizer": ("SANITIZED",)}[stage]
    output = RUN / stage
    if output.exists():
        raise RuntimeError("Stage output exists; no overwrites or replacement runs")
    spec = JudgeSpec.model_validate_json((EXP / "judge_spec.json").read_bytes())
    adapter = OllamaAdapter()
    model = next(m for m in adapter.request("/api/tags")["models"] if m["name"] == spec.model_ref)
    if model["digest"] != MODEL_DIGEST:
        raise RuntimeError("Installed model differs from preregistration")
    fingerprints = {p: sha(ROOT / p) for p in FROZEN}
    if stage != "base" and fingerprints != read(RUN / "base/metadata.json")["input_sha256"]:
        raise RuntimeError("Frozen files changed since base inference")
    show = subprocess.run(["ollama", "show", spec.model_ref], capture_output=True, text=True)
    output.mkdir(parents=True, exist_ok=False)
    write(output / "metadata.json", {
        "schema_version": "1.0", "stage": stage, "code_commit": git("rev-parse", "HEAD"),
        "command": f"PYTHONPATH=src .venv/bin/python scripts/run_probe_pilot_2.py {stage}",
        "working_directory": str(ROOT), "created_at_utc": datetime.now(UTC).isoformat(),
        "model": model, "ollama_version": adapter.request("/api/version"),
        "ollama_show": adapter.request("/api/show", {"model": spec.model_ref}),
        "ollama_show_command": "ollama show llama3.1:8b",
        "ollama_show_cli": {"exit_code": show.returncode, "stdout": show.stdout, "stderr": show.stderr},
        "judge_spec": spec.model_dump(mode="json"), "input_sha256": fingerprints,
        "adapter_version": adapter.version, "seed": 20261018, "num_ctx": 4096, "retries": 0,
        "selected_injection": selected, "total_call_budget": 336,
        "prior_elapsed_seconds": prior_elapsed,
        "selection_sha256": sha(EXP / "sanitizer_selection.json") if selected else None,
    })
    start = time.monotonic()
    calls = 0
    data = reports()
    for condition in conditions:
        for base in data:
            view = transform_2(base, condition, selected).judge_input()
            record = {
                "schema_version": "1.0", "case_id": base.case_id, "condition": condition,
                "selected_injection": selected, "model_digest": MODEL_DIGEST,
                "judge_input": view.model_dump(mode="json"), "raw_response": None,
                "created_at_utc": datetime.now(UTC).isoformat(),
                "verdict": "NOT_RUN", "error_kind": None,
            }
            call_start = time.monotonic()
            if prior_elapsed + call_start - start >= 5400:
                record["not_run_reason"] = "90-minute cumulative live execution budget exhausted"
            else:
                calls += 1
                try:
                    reply = adapter.evaluate(view, spec)
                    record["verdict"] = parse_prediction(reply.text)
                except ContractError:
                    record.update(verdict="ERROR", error_kind="PARSE_ERROR")
                except TimeoutError:
                    record.update(verdict="ERROR", error_kind="TIMEOUT")
                except Exception as exc:
                    record.update(verdict="ERROR", error_kind="PROVIDER_ERROR",
                                  exception_type=type(exc).__name__)
                record["raw_response"] = adapter.last_response
            record["latency_seconds"] = time.monotonic() - call_start
            write(output / f"{condition}--{base.case_id}.json", record)
            print(f"{stage} {calls}/{len(conditions)*48} {condition} {base.case_id}: "
                  f"{record['verdict']}", flush=True)
    write(output / "completion.json", {
        "schema_version": "1.0", "calls": calls, "elapsed_seconds": time.monotonic() - start,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "model_tags_after": adapter.request("/api/tags"),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("base", "probes", "sanitizer"))
    run(parser.parse_args().stage)
