from collections import Counter

from src.sample import allocate, stratified_sample


def rows():
    # 3 categories of uneven size: a=10, b=6, c=4
    return [{"id": f"{cat}{i}", "category": cat} for cat, size in [("a", 10), ("b", 6), ("c", 4)]
            for i in range(size)]


def test_allocate_is_proportional_and_sums_to_n():
    assert allocate({"a": 10, "b": 6, "c": 4}, 10) == {"a": 5, "b": 3, "c": 2}


def test_allocate_distributes_remainder_deterministically():
    counts = allocate({"x": 25, "y": 25, "z": 25}, 10)
    assert sum(counts.values()) == 10
    assert counts == {"x": 4, "y": 3, "z": 3}


def test_allocate_caps_at_total():
    assert sum(allocate({"a": 2, "b": 1}, 50).values()) == 3


def test_sample_is_reproducible_for_a_seed():
    first = stratified_sample(rows(), 10, key="category", seed=1)
    second = stratified_sample(rows(), 10, key="category", seed=1)
    assert first == second


def test_sample_keeps_category_shares():
    picked = stratified_sample(rows(), 10, key="category", seed=7)
    assert Counter(r["category"] for r in picked) == {"a": 5, "b": 3, "c": 2}
    assert len({r["id"] for r in picked}) == 10


def test_different_seeds_give_different_samples():
    a = stratified_sample(rows(), 10, key="category", seed=1)
    b = stratified_sample(rows(), 10, key="category", seed=2)
    assert {r["id"] for r in a} != {r["id"] for r in b}


def test_committed_sample_is_reproducible_from_the_raw_file():
    """Re-running the sampler with the config seed on XSTest gives exactly data/prompts.csv."""
    import csv
    import importlib.util

    import pytest

    from src.config import load_config, resolve

    cfg = load_config()["data"]
    raw = resolve(cfg["raw_path"])
    if not raw.exists():
        pytest.skip("raw XSTest file not downloaded (python scripts/fetch_data.py)")
    spec = importlib.util.spec_from_file_location("fetch_data", resolve("scripts/fetch_data.py"))
    fetch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fetch)
    with open(raw, newline="") as f:
        source = [fetch.to_row(r) for r in csv.DictReader(f)]
    sample = sorted(stratified_sample(source, cfg["sample_size"], key="category", seed=cfg["seed"]),
                    key=lambda r: r["id"])
    with open(resolve(cfg["prompts_path"]), newline="") as f:
        committed = list(csv.DictReader(f))
    assert [r["id"] for r in sample] == [r["id"] for r in committed]
