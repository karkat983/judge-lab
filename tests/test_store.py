from src import store
from src.fake_llm import FakeLLM
from src.judge import Judge, judge_all


def test_judgments_are_saved_as_they_happen(tmp_path):
    path = tmp_path / "results" / "run.jsonl"
    llm = FakeLLM(default='{"verdict": "unsafe", "reason": "harm"}')
    out = judge_all(Judge(llm), [("a", "x"), ("b", "y")], progress=None, save_to=path)
    records = store.read(path)
    assert [r["item_id"] for r in records] == ["a", "b"]
    assert records[0]["verdict"] == "unsafe" and records[0]["raw"].startswith("{")
    assert [store.to_judgment(r) for r in records] == out


def test_reading_a_missing_file_is_empty(tmp_path):
    assert store.read(tmp_path / "nope.jsonl") == []
