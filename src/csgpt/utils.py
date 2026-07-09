"""Utility helpers for the csgpt package."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


def ensure_dir(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def find_files(root: Path, patterns: Iterable[str]) -> List[Path]:
    """Find files matching glob patterns under `root`."""
    out: List[Path] = []
    for p in patterns:
        out.extend(root.glob(p))
    return out
