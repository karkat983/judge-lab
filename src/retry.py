"""Retry transient LLM failures (timeouts, connection resets, 429/5xx) with exponential backoff."""
import random
import time
import urllib.error

TRANSIENT_HTTP = {408, 409, 429, 500, 502, 503, 504}


def is_transient(exc: Exception) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in TRANSIENT_HTTP
    return isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError))


class RetryingClient:
    """Wraps a client; retries `complete` on transient errors, re-raises anything else."""

    def __init__(self, client, attempts: int = 4, base_delay: float = 1.0, max_delay: float = 30.0,
                 sleep=time.sleep):
        self.client = client
        self.attempts = attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.sleep = sleep
        self.retries = 0

    @property
    def model(self):
        return getattr(self.client, "model", None)

    def options(self):
        return self.client.options() if hasattr(self.client, "options") else {}

    def complete(self, system: str, user: str):
        for attempt in range(self.attempts):
            try:
                return self.client.complete(system, user)
            except Exception as exc:
                if not is_transient(exc) or attempt == self.attempts - 1:
                    raise
                self.retries += 1
                delay = min(self.base_delay * 2**attempt, self.max_delay)
                self.sleep(delay * (0.5 + random.random() / 2))    # jitter avoids synchronized retries
        raise AssertionError("unreachable")
