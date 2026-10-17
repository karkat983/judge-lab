"""Review reproduction in a disposable directory only; no real user files touched.

Run with the installed package. A simulated second writer creates the target after
validation but before installation. This illustrates the unsupported concurrent
writer boundary and checks whether an unrelated sentinel survives.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from judge_lab.artifacts import write_bundle


def reproduce() -> dict[str, bool]:
    original_mkdtemp = tempfile.mkdtemp
    with tempfile.TemporaryDirectory(prefix="judge-lab-review-", dir="/private/tmp") as directory:
        target = Path(directory) / "output"
        raced = False

        def raced_mkdtemp(*args, **kwargs):
            nonlocal raced
            stage = original_mkdtemp(*args, **kwargs)
            if not raced:
                raced = True
                target.mkdir()
                (target / "unrelated-sentinel").write_text("synthetic-review-only", encoding="utf-8")
            return stage

        with patch("judge_lab.artifacts.tempfile.mkdtemp", side_effect=raced_mkdtemp):
            write_bundle(target, {"report.json": b"{}"}, overwrite=False)
        return {"unrelated_file_preserved": (target / "unrelated-sentinel").exists(),
                "new_report_installed": (target / "report.json").exists()}


if __name__ == "__main__":
    print(json.dumps(reproduce(), sort_keys=True))
