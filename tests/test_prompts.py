from src.prompts import load_prompt, prompt_hash


def test_judge_v1_asks_for_json_with_both_labels():
    text = load_prompt("judge_v1")
    assert '"verdict"' in text and '"reason"' in text
    assert '"safe"' in text and '"unsafe"' in text


def test_hash_is_short_and_content_based():
    assert len(prompt_hash("x")) == 12
    assert prompt_hash("x") != prompt_hash("y")
