"""The judge's structured output."""
from dataclasses import dataclass

VERDICTS = ("safe", "unsafe")
INVALID = "invalid"


@dataclass(frozen=True)
class Verdict:
    verdict: str          # "safe", "unsafe", or "invalid" when the reply could not be read
    reason: str = ""

    def __post_init__(self):
        if self.verdict not in (*VERDICTS, INVALID):
            raise ValueError(f"verdict must be one of {VERDICTS} or {INVALID!r}, got {self.verdict!r}")

    @property
    def valid(self) -> bool:
        return self.verdict in VERDICTS
