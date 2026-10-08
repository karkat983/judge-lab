"""Read a judge reply into a Verdict."""
import json
import re

from src.verdict import VERDICTS, Verdict

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _json_objects(text: str):
    yield from FENCE.findall(text)
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0:
                yield text[start:i + 1]


def parse_strict(raw: str) -> Verdict | None:
    """The first JSON object whose "verdict" is safe/unsafe (case and spaces ignored), else None."""
    for candidate in _json_objects(raw):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("verdict"), str):
            label = obj["verdict"].strip().lower()
            if label in VERDICTS:
                return Verdict(label, str(obj.get("reason", "")).strip())
    return None

