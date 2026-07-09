"""Repository helpers (placeholders).

This module will provide repository operations (clone, pull, etc.) in the future.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Repository:
    """Represents a code repository.

    Attributes:
        path: Path - local path
        remote: Optional[str] - remote URL
    """

    path: Path
    remote: Optional[str] = None

    def clone(self) -> None:
        """Clone the repository. Not implemented."""
        raise NotImplementedError()

    def pull(self) -> None:
        """Update repository. Not implemented."""
        raise NotImplementedError()
