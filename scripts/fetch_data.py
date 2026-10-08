"""Download XSTest and write a stratified sample to data/prompts.csv.

XSTest (Röttger et al. 2024, CC BY 4.0) has 450 prompts: 250 safe prompts that
look risky and 200 unsafe contrast prompts, each with a human safe/unsafe label.

    python scripts/fetch_data.py
"""
import csv
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src.config import load_config, resolve  # noqa: E402
from src.sample import deduplicate, stratified_sample  # noqa: E402

FIELDS = ["id", "text", "human_label", "category", "focus"]


def download(url: str, dest: pathlib.Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp:
        dest.write_bytes(resp.read())


def to_row(raw: dict) -> dict:
    return {
        "id": f"xstest-{int(raw['id']):03d}",
        "text": raw["prompt"].strip(),
        "human_label": raw["label"].strip(),
        "category": raw["type"].strip(),
        "focus": raw["focus"].strip(),
    }


def main() -> None:
    cfg = load_config()["data"]
    raw_path = resolve(cfg["raw_path"])
    if not raw_path.exists():
        download(cfg["source_url"], raw_path)
    with open(raw_path, newline="") as f:
        rows = [to_row(r) for r in csv.DictReader(f)]
    rows, dropped = deduplicate(rows)
    for dup, original in dropped:
        print(f"dropped {dup}: same text as {original}")

    sample = stratified_sample(rows, cfg["sample_size"], key="category", seed=cfg["seed"])
    sample.sort(key=lambda r: r["id"])

    out = resolve(cfg["prompts_path"])
    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sample)
    safe = sum(r["human_label"] == "safe" for r in sample)
    print(f"wrote {len(sample)} prompts to {out} ({safe} safe, {len(sample) - safe} unsafe)")


if __name__ == "__main__":
    main()
