"""Configuration dataclasses and helpers."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Application configuration.

    Attributes:
        project_root: Path
        github_token: Optional[str]
    """

    project_root: Path
    github_token: Optional[str] = None

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from a file. Not implemented."""
        raise NotImplementedError()
