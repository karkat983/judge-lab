import pytest

from src.fake_llm import FakeLLM
from src.ratelimit import RateLimitedClient


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.slept = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.slept.append(round(seconds, 6))
        self.now += seconds


def test_calls_are_spaced_by_the_interval():
    t = FakeClock()
    client = RateLimitedClient(FakeLLM(), per_second=4, clock=t.clock, sleep=t.sleep)
    for _ in range(4):
        client.complete("s", "u")
    assert t.slept == [0.25, 0.25, 0.25]          # first call is immediate
    assert t.now == pytest.approx(0.75)


def test_no_wait_when_calls_are_already_slow():
    t = FakeClock()
    client = RateLimitedClient(FakeLLM(), per_second=10, clock=t.clock, sleep=t.sleep)
    client.complete("s", "u")
    t.now += 1.0
    client.complete("s", "u")
    assert t.slept == []


def test_rate_must_be_positive():
    with pytest.raises(ValueError):
        RateLimitedClient(FakeLLM(), per_second=0)
