"""Raw judgments as JSON lines: one line per (run, item), written as soon as it is judged."""
import json
import pathlib

from src.judge import Judgment
from src.verdict import Verdict


def to_record(j: Judgment, **extra) -> dict:
    return {
        "item_id": j.item_id, "verdict": j.verdict.verdict, "reason": j.verdict.reason, "raw": j.raw,
        "model": j.model, "prompt": j.prompt, "prompt_hash": j.prompt_hash, **extra,
    }


def append(path: pathlib.Path | str, j: Judgment, **extra) -> None:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(to_record(j, **extra)) + "\n")


def read(path: pathlib.Path | str) -> list[dict]:
    path = pathlib.Path(path)
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def to_judgment(record: dict) -> Judgment:
    return Judgment(record["item_id"], Verdict(record["verdict"], record["reason"]), record["raw"],
                    record["model"], record["prompt"], record["prompt_hash"])
