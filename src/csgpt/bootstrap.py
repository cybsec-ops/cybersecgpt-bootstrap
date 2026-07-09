"""Bootstrap orchestration placeholders (no business logic).

This module is intentionally empty of implementation; it provides stubs
and dataclasses to be filled in later.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Bootstrapper:
    """Coordinates bootstrap operations.

    Attributes:
        project_root: Path - root path of the project
    """

    project_root: Path

    def run(self) -> None:
        """Run bootstrap process. Not implemented in scaffold."""
        logger.debug("Bootstrapper.run called for %s", self.project_root)
        raise NotImplementedError("Bootstrap logic not implemented")
