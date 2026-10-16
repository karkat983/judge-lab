"""Pure answered-case statistics with explicit denominators and Wilson uncertainty."""

import math
from typing import Literal

from judge_lab.contracts import ContractError, Count, FrozenModel, JudgeResult, RunManifest
from judge_lab.load import LoadedDataset
from judge_lab.runner import validate_results
from judge_lab.serialization import digest


class Metric(FrozenModel):
    numerator: Count
    denominator: Count
    value: float | None
    undefined_reason: Literal["ZERO_DENOMINATOR"] | None
    wilson_95: tuple[float, float] | None
    interval_reason: Literal["ZERO_DENOMINATOR", "CORRELATED_FAMILIES"] | None


class Statistics(FrozenModel):
    counts: dict[str, int]
    denominators: dict[str, int]
    metrics: dict[str, Metric]
    kappa: float | None
    kappa_reason: Literal["NO_ANSWERS", "EXPECTED_AGREEMENT_ONE"] | None
    independent_families: int
    correlated_cases: bool
    small_sample: bool


def wilson(successes: int, n: int) -> tuple[float, float] | None:
    if type(successes) is not int or type(n) is not int or not 0 <= successes <= n:
        raise ContractError("INVALID_INPUT")
    if n == 0:
        return None
    z = 1.959963984540054
    p, z2 = successes / n, z * z
    center = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return max(0.0, center - half), min(1.0, center + half)


def _ratio(k: int, n: int, correlated: bool) -> Metric:
    return Metric(
        numerator=k, denominator=n, value=k / n if n else None,
        undefined_reason=None if n else "ZERO_DENOMINATOR",
        wilson_95=wilson(k, n) if not correlated else None,
        interval_reason="CORRELATED_FAMILIES" if correlated else (None if n else "ZERO_DENOMINATOR"),
    )


def binary_statistics(references: tuple[str, ...], predictions: tuple[str, ...],
                      families: tuple[str, ...] | None = None) -> Statistics:
    if len(references) != len(predictions):
        raise ContractError("INVALID_INPUT")
    if families is None:
        families = tuple(str(i) for i in range(len(references)))
    if len(families) != len(references) or any(not f for f in families):
        raise ContractError("INVALID_INPUT")
    counts = dict.fromkeys(("AA", "AR", "RA", "RR", "A?", "R?", "AE", "RE"), 0)
    columns = {"ACCEPT": "A", "REJECT": "R", "ABSTAIN": "?", "ERROR": "E"}
    for reference, prediction in zip(references, predictions, strict=True):
        if reference not in ("ACCEPT", "REJECT") or prediction not in columns:
            raise ContractError("INVALID_INPUT")
        counts[reference[0] + columns[prediction]] += 1
    aa, ar, ra, rr = (counts[key] for key in ("AA", "AR", "RA", "RR"))
    n, total, correct = aa + ar + ra + rr, len(references), aa + rr
    rejects = ra + rr + counts["R?"] + counts["RE"]
    accepts = aa + ar + counts["A?"] + counts["AE"]
    correlated = len(set(families)) < total
    definitions = {
        "coverage": (n, total), "conditional_accuracy": (correct, n),
        "all_case_correctness": (correct, total), "false_accept_rate_on_rejects": (ra, ra + rr),
        "false_accept_rate_all_rejects": (ra, rejects),
        "false_reject_rate_on_accepts": (ar, aa + ar),
        "false_reject_rate_all_accepts": (ar, accepts), "safe_case_accept_precision": (aa, aa + ra),
    }
    expected_numerator = (aa + ar) * (aa + ra) + (ra + rr) * (ar + rr)
    kappa_denominator = n * n - expected_numerator
    kappa = ((correct * n - expected_numerator) / kappa_denominator) if kappa_denominator else None
    return Statistics(
        counts=counts,
        denominators={"eligible_total": total, "evaluated_valid": n, "reference_accept": accepts,
                      "reference_reject": rejects, "answered_accept": aa + ar, "answered_reject": ra + rr},
        metrics={key: _ratio(k, d, correlated) for key, (k, d) in definitions.items()},
        kappa=kappa, kappa_reason=None if kappa is not None else (
            "NO_ANSWERS" if not n else "EXPECTED_AGREEMENT_ONE"),
        independent_families=len(set(families)), correlated_cases=correlated, small_sample=total < 30,
    )


def calibrate(dataset: LoadedDataset, results: tuple[JudgeResult, ...], run: RunManifest) -> Statistics:
    ordered = validate_results(dataset, run, results)
    cases = {case.case_id: case for case in dataset.cases}
    return binary_statistics(
        tuple(cases[r.case_id].reference_label for r in ordered), tuple(r.verdict for r in ordered),
        tuple(cases[r.case_id].case_family_id for r in ordered),
    )


def slice_statistics(dataset: LoadedDataset, results: tuple[JudgeResult, ...],
                     run: RunManifest) -> dict[str, Statistics]:
    ordered = validate_results(dataset, run, results)
    cases = {case.case_id: case for case in dataset.cases}
    groups: dict[str, list[JudgeResult]] = {}
    for result in ordered:
        case = cases[result.case_id]
        keys = ["family:" + digest(case.case_family_id)]
        keys += ["defect:" + digest(reason) for reason in case.reference_reason_codes]
        for key in keys:
            groups.setdefault(key, []).append(result)
    return {key: binary_statistics(
        tuple(cases[r.case_id].reference_label for r in group), tuple(r.verdict for r in group),
        tuple(cases[r.case_id].case_family_id for r in group),
    ) for key, group in sorted(groups.items())}
