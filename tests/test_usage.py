import pytest

from src.llm import LLMResponse
from src.usage import MeteredClient


class Stub:
    model = "claude-opus-5-5"

    def complete(self, system, user):
        return LLMResponse(text="ok", model=self.model, input_tokens=500, output_tokens=50)


def test_cost_of_judging_100_items_on_claude():
    meter = MeteredClient(Stub())
    for _ in range(100):
        meter.complete("rubric", "item")
    # 100 * (500 * $4/M + 50 * $20/M) = 100 * 0.003 = $0.30
    assert meter.total_cost_usd() == pytest.approx(0.30)


def test_local_model_is_free_but_counted():
    stub = Stub()
    stub.model = "qwen2.5:3b-instruct"
    meter = MeteredClient(stub)
    meter.complete("r", "i")
    assert meter.by_model["qwen2.5:3b-instruct"].calls == 1
    assert meter.total_cost_usd() == 0
