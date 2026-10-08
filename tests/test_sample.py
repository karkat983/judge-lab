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
