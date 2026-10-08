"""Deterministic stratified sampling, so every category keeps its share."""
import math
import random
import re
import unicodedata
from collections import defaultdict


def allocate(group_sizes: dict[str, int], n: int) -> dict[str, int]:
    """Split n across groups in proportion to their size (largest-remainder method).

    The result always sums to n (or to the total, if n exceeds it).
    """
    total = sum(group_sizes.values())
    n = min(n, total)
    quotas = {g: n * size / total for g, size in group_sizes.items()}
    counts = {g: math.floor(q) for g, q in quotas.items()}
    leftover = n - sum(counts.values())
    # Ties broken by group name so the allocation never depends on dict order.
    by_remainder = sorted(quotas, key=lambda g: (-(quotas[g] - counts[g]), g))
    for g in by_remainder[:leftover]:
        counts[g] += 1
    return counts


def stratified_sample(rows: list[dict], n: int, key: str, seed: int) -> list[dict]:
    """Sample n rows, stratified by rows[key], reproducible for a given seed."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    counts = allocate({g: len(rs) for g, rs in groups.items()}, n)
    rng = random.Random(seed)
    picked = []
    for g in sorted(groups):
        picked.extend(rng.sample(groups[g], counts[g]))
    return picked


def normalise(text: str) -> str:
    """Text used to detect duplicates: case-folded, accents and punctuation removed, spaces collapsed."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s]", " ", text.casefold())
    return " ".join(text.split())


def deduplicate(rows: list[dict], key: str = "text") -> tuple[list[dict], list[tuple[str, str]]]:
    """Keep the first row of each normalised text. Returns (kept rows, [(dropped id, kept id)])."""
    seen: dict[str, str] = {}
    kept, dropped = [], []
    for row in rows:
        norm = normalise(row[key])
        if norm in seen:
            dropped.append((row["id"], seen[norm]))
        else:
            seen[norm] = row["id"]
            kept.append(row)
    return kept, dropped
