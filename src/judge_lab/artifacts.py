"""Atomic owned output bundles. Never follow symlinks or erase an unrelated directory."""

import os
import shutil
import tempfile
from pathlib import Path

from judge_lab.contracts import ContractError

MARKER = b"judge-lab-owned-bundle-v1\n"


def write_bundle(output: Path, files: dict[str, bytes], *, overwrite: bool = False) -> None:
    if ".." in output.parts or output == Path("."):
        raise ContractError("INVALID_INPUT")
    target = output.absolute()
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ContractError("INVALID_INPUT")
    if any(Path(name).name != name or name in ("", ".", "..", ".judge-lab") for name in files):
        raise ContractError("INVALID_INPUT")
    if target.exists():
        if not overwrite or not target.is_dir():
            raise ContractError("INVALID_INPUT")
        marker = target / ".judge-lab"
        if (marker.is_symlink() or not marker.is_file() or marker.read_bytes() != MARKER
                or any(p.is_symlink() or p.is_dir() for p in target.iterdir())):
            raise ContractError("INVALID_INPUT")
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".judge-lab-", dir=target.parent))
    backup: Path | None = None
    try:
        for name, content in {**files, ".judge-lab": MARKER}.items():
            with (stage / name).open("xb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        if target.exists():
            backup = Path(tempfile.mkdtemp(prefix=".judge-lab-backup-", dir=target.parent))
            backup.rmdir()
            target.rename(backup)
        stage.rename(target)
    except OSError:
        if backup is not None and not target.exists():
            backup.rename(target)
        raise ContractError("INVALID_INPUT") from None
    finally:
        if stage.exists():
            shutil.rmtree(stage)
        if backup is not None and backup.exists() and target.exists():
            shutil.rmtree(backup)
