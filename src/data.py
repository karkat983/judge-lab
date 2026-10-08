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


# XSTest pairs each safe category with an unsafe "contrast_" twin built from the same trigger
# words. Two families have more than one safe set sharing one contrast set.
DISCRIMINATION = {"nons_group_real_discr", "real_group_nons_discr", "contrast_discr"}
PRIVACY = {"privacy_public", "privacy_fictional", "contrast_privacy"}


def topic_of(category: str) -> str:
    if category in DISCRIMINATION:
        return "discrimination"
    if category in PRIVACY:
        return "privacy"
    return category.removeprefix("contrast_")


def add_category_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Add `topic` (the safe/unsafe pair a category belongs to) and `is_contrast` columns."""
    out = df.copy()
    out["is_contrast"] = out["category"].str.startswith("contrast_")
    out["topic"] = out["category"].map(topic_of)
    return out
