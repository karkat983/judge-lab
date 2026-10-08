import pathlib

import pytest

from src.data import load_prompts

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def prompts():
    """The committed 200-prompt XSTest sample."""
    return load_prompts(ROOT / "data" / "prompts.csv")
