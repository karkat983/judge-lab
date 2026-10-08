"""Cap the request rate to a provider (thread-safe), for APIs with per-minute limits."""
import threading
import time


class RateLimitedClient:
    """Allows at most `per_second` calls per second across all threads, by spacing call starts."""

    def __init__(self, client, per_second: float, clock=time.monotonic, sleep=time.sleep):
        if per_second <= 0:
            raise ValueError("per_second must be positive")
        self.client = client
        self.interval = 1.0 / per_second
        self.clock = clock
        self.sleep = sleep
        self._next = 0.0
        self._lock = threading.Lock()

    @property
    def model(self):
        return getattr(self.client, "model", None)

    def options(self):
        return self.client.options() if hasattr(self.client, "options") else {}

    def _wait_turn(self) -> None:
        with self._lock:
            now = self.clock()
            start = max(now, self._next)
            self._next = start + self.interval
        if start > now:
            self.sleep(start - now)

    def complete(self, system: str, user: str):
        self._wait_turn()
        return self.client.complete(system, user)
