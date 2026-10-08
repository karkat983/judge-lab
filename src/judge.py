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


def judge_all(judge: Judge, items: Iterable[tuple[str, str]], progress=sys.stderr,
              save_to=None) -> list[Judgment]:
    """Judge (id, text) items in order, printing a progress line every 20 items.

    With `save_to`, each judgment is appended to that JSONL file as soon as it exists, so a long
    run leaves a complete record even if it is interrupted. Re-running with the same file
    resumes: items already in it are loaded, not judged again.
    """
    from src import store

    items = list(items)
    done = {r["item_id"]: store.to_judgment(r) for r in store.read(save_to)} if save_to else {}
    out = []
    for i, (item_id, text) in enumerate(items, 1):
        if item_id in done:
            out.append(done[item_id])
        else:
            judgment = judge.judge(item_id, text)
            out.append(judgment)
            if save_to:
                store.append(save_to, judgment)
        if progress and (i % 20 == 0 or i == len(items)):
            invalid = sum(not j.verdict.valid for j in out)
            print(f"judged {i}/{len(items)} ({invalid} invalid)", file=progress, flush=True)
    return out


def judge_parallel(judge: Judge, items: Iterable[tuple[str, str]], workers: int = 4, save_to=None,
                   progress=sys.stderr) -> list[Judgment]:
    """Like judge_all, but judges up to `workers` items at once. Results keep input order, and the
    file is written from the main thread only (in completion order), so resume still works."""
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from src import store

    items = list(items)
    done = {r["item_id"]: store.to_judgment(r) for r in store.read(save_to)} if save_to else {}
    todo = [(item_id, text) for item_id, text in items if item_id not in done]
    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(judge.judge, item_id, text): item_id for item_id, text in todo}
        for n, future in enumerate(as_completed(futures), 1):
            judgment = future.result()
            with lock:
                done[judgment.item_id] = judgment
                if save_to:
                    store.append(save_to, judgment)
            if progress and (n % 20 == 0 or n == len(todo)):
                print(f"judged {n}/{len(todo)} new items", file=progress, flush=True)
    return [done[item_id] for item_id, _ in items]
