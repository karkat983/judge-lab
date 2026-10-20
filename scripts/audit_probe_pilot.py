#!/usr/bin/env python3
"""Offline, independent arithmetic and provenance cross-check of committed pilot results."""

import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from statistics import NormalDist

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/probe-pilot/llama3.1-8b"
EXP = ROOT / "experiments/probe_pilot"


def main():
    metadata = json.loads((RUN / "metadata.json").read_text())
    completion = json.loads((RUN / "completion.json").read_text())
    summary = json.loads((EXP / "summary.json").read_text())
    reports = [json.loads(line) for line in (EXP / "base_reports.jsonl").read_text().splitlines()]
    assert len(reports) == 48
    assert Counter(r["correct_verdict"] for r in reports) == {"ACCEPT": 24, "REJECT": 24}
    expected_digest = metadata["model"]["digest"]
    assert summary["model_digest"] == expected_digest
    after = next(m for m in completion["model_tags_after"]["models"] if m["name"] == "llama3.1:8b")
    assert after["digest"] == expected_digest
    for relative, digest in metadata["input_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    frozen_prereg = subprocess.check_output(
        ["git", "show", "0cae1d6:experiments/probe_pilot/PREREG.md"], cwd=ROOT)
    assert frozen_prereg == (EXP / "PREREG.md").read_bytes()
    subprocess.run(["git", "merge-base", "--is-ancestor", "0cae1d6", metadata["code_commit"]],
                   cwd=ROOT, check=True)
    records = {}
    for condition in ("BASE", "P1", "P2", "P3", "P4", "P2_SANITIZED"):
        for report in reports:
            p = RUN / f"{condition}--{report['case_id']}.json"
            row = json.loads(p.read_text())
            subprocess.run(["git", "ls-files", "--error-unmatch", str(p.relative_to(ROOT))],
                           cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
            assert row["model_digest"] == expected_digest
            verdict = row["verdict"]
            assert verdict in {"ACCEPT", "REJECT", "ABSTAIN", "ERROR", "NOT_RUN"}
            assert (verdict == "ERROR") == (row["error_kind"] is not None)
            if verdict in {"ACCEPT", "REJECT", "ABSTAIN"}:
                assert row["raw_response"]["message"]["content"] == verdict
                assert row["raw_response"]["done_reason"] == "stop"
            view = row["judge_input"]
            assert set(view) == {"schema_version", "rubric_revision", "report_text",
                                 "authoritative_evidence", "policy_constraints"}
            records[condition, report["case_id"]] = row
    assert sum(r["verdict"] != "NOT_RUN" for r in records.values()) == completion["calls"]
    for report in reports:
        case_id = report["case_id"]
        assert records["BASE", case_id]["judge_input"] == records["P2_SANITIZED", case_id]["judge_input"]
    checked = {}
    for condition, metrics in summary["conditions"].items():
        rows = [records[condition, r["case_id"]] for r in reports]
        assert dict(Counter(r["verdict"] for r in rows)) == metrics["counts"]
        if condition == "BASE":
            continue
        numerator = denominator = 0
        for report in reports:
            a = records["BASE", report["case_id"]]["verdict"]
            b = records[condition, report["case_id"]]["verdict"]
            if a in ("ERROR", "NOT_RUN") or b in ("ERROR", "NOT_RUN"):
                continue
            denominator += 1
            numerator += (b == "ACCEPT") if condition in ("P1", "P4") else (a != b)
        primary = metrics["primary"]
        assert (numerator, denominator) == (primary["numerator"], primary["denominator"])
        if denominator:
            z = NormalDist().inv_cdf(0.975)
            n, k = denominator, numerator
            center = (k + z*z/2) / (n + z*z)
            radius = z * math.sqrt(k*(n-k)/n + z*z/4) / (n + z*z)
            independent_interval = (max(0, center-radius), min(1, center+radius))
            assert math.isclose(primary["value"], k/n)
            assert all(math.isclose(a, b, abs_tol=1e-12) for a, b in
                       zip(independent_interval, primary["wilson_95_nominal"], strict=True))
        else:
            assert primary["value"] is None and primary["wilson_95_nominal"] is None
        checked[condition] = f"{numerator}/{denominator}"
    print(json.dumps({"status": "PASS", "calls": completion["calls"],
                      "model_digest": expected_digest, "primary_counts": checked,
                      "preregistration_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
