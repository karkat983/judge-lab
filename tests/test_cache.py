from src.cache import CachedClient, cache_key
from src.llm import LLMResponse


class CountingClient:
    model = "judge-1"

    def __init__(self):
        self.calls = 0

    def options(self):
        return {"temperature": 0}

    def complete(self, system, user):
        self.calls += 1
        return LLMResponse(text='{"verdict": "safe"}', model=self.model, input_tokens=30, output_tokens=6)


def test_identical_judgment_is_served_from_disk(tmp_path):
    inner = CountingClient()
    cached = CachedClient(inner, tmp_path)
    assert cached.complete("rubric", "prompt") == cached.complete("rubric", "prompt")
    assert inner.calls == 1


def test_changed_rubric_or_prompt_misses(tmp_path):
    inner = CountingClient()
    cached = CachedClient(inner, tmp_path)
    cached.complete("rubric v1", "p")
    cached.complete("rubric v2", "p")
    cached.complete("rubric v1", "p2")
    assert inner.calls == 3


def test_key_depends_on_sampling_options():
    a = cache_key({"model": "m", "options": {"temperature": 0}}, "s", "u")
    assert a != cache_key({"model": "m", "options": {"temperature": 0.7}}, "s", "u")
