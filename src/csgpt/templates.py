"""Template utilities (placeholders).

Template rendering (e.g., jinja2) will be integrated later.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class TemplateManager:
    """Manage project templates.

    Attributes:
        templates_dir: Path
    """

    templates_dir: Path

    def list(self) -> Iterable[str]:
        """List available templates. Not implemented."""
        raise NotImplementedError()

    def render(self, name: str, destination: Path) -> None:
        """Render template to destination. Not implemented."""
        raise NotImplementedError()
