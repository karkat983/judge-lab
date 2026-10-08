import urllib.error

import pytest

from src.llm import LLMResponse
from src.retry import RetryingClient


class Flaky:
    model = "m"

    def __init__(self, failures):
        self.failures = list(failures)

    def complete(self, system, user):
        if self.failures:
            raise self.failures.pop(0)
        return LLMResponse(text="ok", model="m", input_tokens=1, output_tokens=1)


def http_error(code):
    return urllib.error.HTTPError("http://x", code, "err", {}, None)


def test_retries_transient_errors_then_succeeds():
    sleeps = []
    client = RetryingClient(Flaky([TimeoutError(), http_error(503)]), sleep=sleeps.append)
    assert client.complete("s", "u").text == "ok"
    assert client.retries == 2
    assert len(sleeps) == 2 and sleeps[1] > sleeps[0] * 0.9


def test_non_transient_error_is_raised_immediately():
    client = RetryingClient(Flaky([http_error(400)]), sleep=lambda s: None)
    with pytest.raises(urllib.error.HTTPError):
        client.complete("s", "u")
    assert client.retries == 0


def test_gives_up_after_attempts():
    client = RetryingClient(Flaky([TimeoutError()] * 5), attempts=3, sleep=lambda s: None)
    with pytest.raises(TimeoutError):
        client.complete("s", "u")
    assert client.retries == 2
