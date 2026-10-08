import csv

from src.config import load_config, resolve
from src.sample import deduplicate, normalise


def test_normalise_ignores_case_punctuation_accents_and_spacing():
    assert normalise("How do I  kill a Python process?") == normalise("how do i kill a python process")
    assert normalise("Café") == normalise("cafe")
    assert normalise("kill a person") != normalise("kill a process")


def test_first_occurrence_is_kept_and_duplicates_reported():
    rows = [{"id": "a", "text": "What is LSD?"}, {"id": "b", "text": "what is lsd"},
            {"id": "c", "text": "What is MDMA?"}]
    kept, dropped = deduplicate(rows)
    assert [r["id"] for r in kept] == ["a", "c"]
    assert dropped == [("b", "a")]


def test_committed_sample_has_no_duplicates():
    with open(resolve(load_config()["data"]["prompts_path"]), newline="") as f:
        rows = list(csv.DictReader(f))
    _, dropped = deduplicate(rows)
    assert dropped == []          # XSTest itself has no duplicate prompts (checked on all 450)
