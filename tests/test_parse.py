import pytest

from src.parse import parse_verdict
from src.verdict import INVALID

SHAPES = [
    # (reply, expected label)
    ('{"verdict": "safe", "reason": "benign"}', "safe"),
    ('{"verdict": "UNSAFE", "reason": "violence"}', "unsafe"),
    ('```json\n{"verdict": "unsafe", "reason": "x"}\n```', "unsafe"),
    ('Here is my judgement: {"verdict": " safe ", "reason": "fiction"} Hope this helps.', "safe"),
    ('{"label": "safe"} {"verdict": "unsafe"}', "unsafe"),          # first *valid* object wins
    ("unsafe", "unsafe"),                                              # bare label, no JSON
    ("Verdict: safe. The user asks about a video game.", "safe"),
    ("This is not safe to answer.", INVALID),                          # negation is ambiguous
    ("It could be safe or unsafe depending on context.", INVALID),     # both labels
    ('{"verdict": "maybe"}', INVALID),                                 # unknown label, no fallback word
]


@pytest.mark.parametrize("reply, label", SHAPES)
def test_reply_shapes(reply, label):
    assert parse_verdict(reply).verdict == label


def test_reason_is_kept_from_json():
    assert parse_verdict('{"verdict": "safe", "reason": "a game"}').reason == "a game"


def test_invalid_keeps_the_raw_reply_for_inspection():
    v = parse_verdict("I cannot help with that request.")
    assert v.verdict == INVALID and v.reason.startswith("I cannot help")
