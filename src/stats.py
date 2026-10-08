"""Agreement between the judge's verdicts and human labels.

Verdicts outside {safe, unsafe} (e.g. a reply the parser could not read) are
counted in n_invalid and left out of accuracy, kappa and the confusion matrix.
"""
from dataclasses import dataclass

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
