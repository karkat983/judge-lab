"""Agreement between the judge's verdicts and human labels.

Verdicts outside {safe, unsafe} (e.g. a reply the parser could not read) are
counted in n_invalid and left out of accuracy, kappa and the confusion matrix.
"""
from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix

LABELS = ["safe", "unsafe"]   # row/column order of the confusion matrix


@dataclass(frozen=True)
class Agreement:
    n: int                     # pairs scored (valid verdicts only)
    n_invalid: int
    accuracy: float
    kappa: float
    confusion: list[list[int]]  # rows = human label, columns = judge verdict


def agreement(human: list[str], judge: list[str]) -> Agreement:
    if len(human) != len(judge):
        raise ValueError(f"length mismatch: {len(human)} human vs {len(judge)} judge")
    pairs = [(h, j) for h, j in zip(human, judge, strict=True) if j in LABELS]
    if not pairs:
        raise ValueError("no valid judge verdicts")
    h, j = (list(t) for t in zip(*pairs, strict=True))
    return Agreement(
        n=len(pairs),
        n_invalid=len(human) - len(pairs),
        accuracy=float(accuracy_score(h, j)),
        kappa=float(cohen_kappa_score(h, j, labels=LABELS)),
        confusion=confusion_matrix(h, j, labels=LABELS).tolist(),
    )


def bootstrap_kappa_ci(
    human: list[str], judge: list[str], n_boot: int = 2000, level: float = 0.95, seed: int = 0
) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for Cohen's kappa (resampling items).

    Invalid verdicts are dropped first, as in `agreement`. Resamples where kappa is undefined
    (only one label present) are skipped.
    """
    pairs = [(h, j) for h, j in zip(human, judge, strict=True) if j in LABELS]
    if len(pairs) < 2:
        raise ValueError("need at least two valid verdicts")
    h = np.array([p[0] for p in pairs])
    j = np.array([p[1] for p in pairs])
    rng = np.random.default_rng(seed)
    kappas = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(pairs), len(pairs))
        hs, js = h[idx], j[idx]
        if len(set(hs) | set(js)) < 2:
            continue
        k = cohen_kappa_score(hs, js, labels=LABELS)
        if not np.isnan(k):
            kappas.append(k)
    lo, hi = np.quantile(kappas, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(lo), float(hi)
