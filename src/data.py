"""Load data/prompts.csv and check it before any judging run spends API calls."""
import pathlib

import pandas as pd

REQUIRED_COLUMNS = ["id", "text", "human_label", "category"]
LABELS = {"safe", "unsafe"}


class SchemaError(ValueError):
    pass


def validate(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"missing columns: {missing}")
    bad_labels = sorted(set(df["human_label"]) - LABELS)
    if bad_labels:
        raise SchemaError(f"unknown labels: {bad_labels}")
    dupes = df["id"][df["id"].duplicated()].tolist()
    if dupes:
        raise SchemaError(f"duplicate ids: {dupes}")
    empty = df["id"][df["text"].fillna("").str.strip() == ""].tolist()
    if empty:
        raise SchemaError(f"empty text for ids: {empty}")


def load_prompts(path: pathlib.Path | str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    validate(df)
    return df
