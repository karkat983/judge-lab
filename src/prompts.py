"""Judge prompts live in prompts/<name>.txt so they can be versioned and hashed."""
import hashlib
import pathlib

PROMPTS = pathlib.Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPTS / f"{name}.txt").read_text().strip()


def prompt_hash(text: str) -> str:
    """Short content hash, recorded with every judgment."""
    return hashlib.sha256(text.encode()).hexdigest()[:12]
