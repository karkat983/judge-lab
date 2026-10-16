"""Offline adapters, strict parsing, bounded execution and exact prediction joins."""

import multiprocessing
import time
from collections.abc import Callable
from dataclasses import dataclass
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Protocol

from judge_lab.contracts import (
    Case,
    ContractError,
    ErrorKind,
    JudgeInput,
    JudgeResult,
    JudgeSpec,
    Prediction,
    RunManifest,
)
from judge_lab.load import MAX_DATASET_BYTES, LoadedDataset, read_bounded, verify_dataset
from judge_lab.provenance import verify_result, verify_run_manifest
from judge_lab.serialization import decode_model, digest


@dataclass(frozen=True)
class AdapterReply:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float | None = 0.0


class JudgeAdapter(Protocol):
    version: str

    def evaluate(self, case: JudgeInput, spec: JudgeSpec) -> AdapterReply: ...


class DeterministicMockAdapter:
    """A narrow synthetic test double; rules are not a semantic quality evaluator."""

    version = "mock-rules-v1"

    def evaluate(self, case: JudgeInput, spec: JudgeSpec) -> AdapterReply:
        text = case.report_text.lower()
        bad = ("ghost-9" in text or "restart production cedar immediately" in text
               or "delete all production" in text or "there is no uncertainty" in text
               or "log-1" not in text)
        return AdapterReply("REJECT" if bad else "ACCEPT")


def parse_prediction(raw: str) -> Prediction:
    # Deliberately no extraction, trimming, case folding or prose fallback.
    if raw == "ACCEPT":
        return "ACCEPT"
    if raw == "REJECT":
        return "REJECT"
    if raw == "ABSTAIN":
        return "ABSTAIN"
    raise ContractError("PARSE_ERROR")


def _child(adapter: JudgeAdapter, view: JudgeInput, spec: JudgeSpec, connection: Connection) -> None:
    try:
        reply = adapter.evaluate(view, spec)
        # Only trusted locally installed adapters execute; no source code is loaded from data.
        connection.send(reply)
    except Exception:
        connection.send(None)  # Never propagate exception strings or traceback locals.
    finally:
        connection.close()


def _bounded_call(adapter: JudgeAdapter, view: JudgeInput, spec: JudgeSpec,
                  cancelled: Callable[[], bool]) -> AdapterReply:
    context = multiprocessing.get_context("spawn")
    reader, writer = context.Pipe(duplex=False)
    process = context.Process(target=_child, args=(adapter, view, spec, writer), daemon=True)
    deadline = time.monotonic() + spec.limits.timeout_seconds
    try:
        process.start()
        writer.close()
        while not reader.poll(min(0.02, max(0.0, deadline - time.monotonic()))):
            if cancelled() or time.monotonic() >= deadline:
                raise TimeoutError
            if not process.is_alive():
                raise RuntimeError
        reply = reader.recv()
        if not isinstance(reply, AdapterReply):
            raise RuntimeError
        return reply
    finally:
        if process.is_alive():
            process.terminate()
        if process.pid is not None:
            process.join(timeout=1)
        reader.close()
        writer.close()


def bind_result(case: Case, run: RunManifest, reply: AdapterReply | None = None,
                error: ErrorKind | None = None, latency_ms: float = 0) -> JudgeResult:
    verdict: Prediction | str = "ERROR"
    if reply is not None and error is None:
        try:
            verdict = parse_prediction(reply.text)
        except ContractError:
            error = "PARSE_ERROR"
    return JudgeResult.model_validate({
        "schema_version": "1.0", "case_id": case.case_id, "case_digest": digest(case),
        "run_id": run.run_id, "judge_spec_digest": run.judge_spec_digest,
        "verdict": verdict, "error_kind": error, "latency_ms": latency_ms,
        "input_tokens": reply.input_tokens if reply else 0,
        "output_tokens": reply.output_tokens if reply else 0,
        "estimated_cost_usd": reply.estimated_cost_usd if reply else None,
    })


def run_judge(dataset: LoadedDataset, spec: JudgeSpec, run: RunManifest,
              adapter: JudgeAdapter | None = None,
              cancelled: Callable[[], bool] = lambda: False) -> tuple[JudgeResult, ...]:
    verify_dataset(dataset)
    verify_run_manifest(run)
    adapter = adapter or DeterministicMockAdapter()
    if (spec.adapter != "deterministic_mock" or run.adapter_version != adapter.version
            or run.judge_spec_digest != digest(spec) or run.dataset_digest != dataset.manifest.sha256
            or run.dataset_manifest_digest != digest(dataset.manifest)):
        raise ContractError("INTEGRITY_ERROR")
    # No cost-bearing adapters are executable yet. Future providers need reservation accounting.
    calls, spent, halted = 0, 0.0, False
    results = []
    for case in sorted(dataset.cases, key=lambda c: c.case_id):
        if halted or cancelled() or calls >= spec.limits.max_calls:
            results.append(bind_result(case, run, error="BUDGET_EXCEEDED"))
            continue
        calls += 1
        start = time.monotonic()
        try:
            if type(adapter) is DeterministicMockAdapter:
                reply = adapter.evaluate(case.judge_input(), spec)
                latency = 0.0  # Stable synthetic logical timing, not a benchmark.
            else:
                reply = _bounded_call(adapter, case.judge_input(), spec, cancelled)
                latency = (time.monotonic() - start) * 1000
            result = bind_result(case, run, reply, latency_ms=latency)
            if result.estimated_cost_usd is None or result.estimated_cost_usd > 0:
                # Custom adapters are offline test doubles only; never authorize paid execution.
                halted = True
                result = bind_result(case, run, reply, "BUDGET_EXCEEDED", latency)
            spent += result.estimated_cost_usd or 0.0
            if spent > spec.limits.max_cost_usd:
                halted = True
        except TimeoutError:
            halted = True
            result = bind_result(case, run, error="TIMEOUT")
        except Exception:
            result = bind_result(case, run, error="PROVIDER_ERROR")
        results.append(result)
    return tuple(results)


def validate_results(dataset: LoadedDataset, run: RunManifest,
                     results: tuple[JudgeResult, ...]) -> tuple[JudgeResult, ...]:
    indexed = {result.case_id: result for result in results}
    if len(indexed) != len(results) or set(indexed) != {case.case_id for case in dataset.cases}:
        raise ContractError("INVALID_INPUT")
    for case in dataset.cases:
        verify_result(indexed[case.case_id], case, run, dataset)
    return tuple(indexed[key] for key in sorted(indexed))


def import_predictions(path: Path, dataset: LoadedDataset, run: RunManifest) -> tuple[JudgeResult, ...]:
    raw = read_bounded(path, MAX_DATASET_BYTES)
    results = tuple(decode_model(JudgeResult, line) for line in raw.splitlines())
    return validate_results(dataset, run, results)
