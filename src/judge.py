"""The LLM judge: show it one request, get back a safe/unsafe verdict."""
import sys
from collections.abc import Iterable
from dataclasses import dataclass

from src.parse import parse_verdict
from src.prompts import load_prompt, prompt_hash
from src.verdict import Verdict


@dataclass(frozen=True)
class Judgment:
    item_id: str
    verdict: Verdict
    raw: str               # the judge's full reply, kept for auditing
    model: str
    prompt: str            # prompt name, e.g. judge_v1
    prompt_hash: str


class Judge:
    def __init__(self, llm, prompt: str = "judge_v1"):
        self.llm = llm
        self.prompt = prompt
        self.system = load_prompt(prompt)
        self.hash = prompt_hash(self.system)

    def judge(self, item_id: str, text: str) -> Judgment:
        reply = self.llm.complete(self.system, f"Request:\n{text}")
        return Judgment(item_id, parse_verdict(reply.text), reply.text, reply.model, self.prompt, self.hash)


def judge_all(judge: Judge, items: Iterable[tuple[str, str]], progress=sys.stderr) -> list[Judgment]:
    """Judge (id, text) items in order, printing a progress line every 20 items."""
    items = list(items)
    out = []
    for i, (item_id, text) in enumerate(items, 1):
        out.append(judge.judge(item_id, text))
        if progress and (i % 20 == 0 or i == len(items)):
            invalid = sum(not j.verdict.valid for j in out)
            print(f"judged {i}/{len(items)} ({invalid} invalid)", file=progress, flush=True)
    return out
