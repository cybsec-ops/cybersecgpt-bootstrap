"""Minimal GitHub client placeholders."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class GitHubClient:
    """Placeholder GitHub client.

    Attributes:
        token: Optional[str] - authentication token
    """

    token: Optional[str] = None

    def get_repository(self, owner: str, name: str) -> dict:
        """Return repository metadata. Not implemented."""
        raise NotImplementedError()
