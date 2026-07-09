"""Repository data models and registry support.

This module provides a lightweight repository model and manager for
loading repository registry configuration from YAML.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RepositoryRegistryError(ValueError):
    """Base error for repository registry issues."""


class RepositoryRegistryFileNotFoundError(RepositoryRegistryError):
    """Raised when the repository registry file does not exist."""


class DuplicateRepositoryIdError(RepositoryRegistryError):
    """Raised when duplicate repository ids are detected."""


class DuplicateRepositoryNameError(RepositoryRegistryError):
    """Raised when duplicate repository names are detected."""


class MissingRepositoryFieldError(RepositoryRegistryError):
    """Raised when required repository fields are missing."""


@dataclass
class Repository:
    """Represents a repository registry entry.

    Attributes:
        id: Unique repository identifier.
        name: Human-friendly repository name.
        description: Short repository description.
        category: Repository category, such as core, platform, or tooling.
        active: Whether the repository is active in the workspace.
        path: Local repository path relative to the workspace root.
    """

    id: str
    name: str
    description: str
    category: str
    active: bool
    path: Path

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Repository":
        """Create a Repository instance from a dictionary.

        Args:
            data: Mapping containing repository fields.

        Returns:
            Repository: Parsed repository object.

        Raises:
            MissingRepositoryFieldError: If a required field is absent.
        """
        required_keys = {"id", "name", "description", "category", "active", "path"}
        missing = required_keys - data.keys()
        if missing:
            raise MissingRepositoryFieldError(
                f"Repository entry missing required fields: {sorted(missing)}"
            )

        return cls(
            id=str(data["id"]).strip(),
            name=str(data["name"]).strip(),
            description=str(data["description"]).strip(),
            category=str(data["category"]).strip(),
            active=bool(data["active"]),
            path=Path(str(data["path"])),
        )


class RepositoryManager:
    """Loads and validates a repository registry from YAML."""

    DEFAULT_PATH = Path("configs/repositories.yaml")

    def __init__(self, path: Path | None = None) -> None:
        self.path = (path or self.DEFAULT_PATH).expanduser()
        self.repositories: list[Repository] = []

    def load(self) -> list[Repository]:
        """Load repositories from the registry file.

        Returns:
            List[Repository]: Parsed repository registry entries.

        Raises:
            RepositoryRegistryFileNotFoundError: If the file does not exist.
            RepositoryRegistryError: For parse, validation, or schema errors.
        """
        raw = self._load_registry()
        repositories = self._validate_registry_root(raw)
        self.repositories = self._parse_repositories(repositories)
        return self.repositories

    def _load_registry(self) -> Any:
        if not self.path.exists():
            raise RepositoryRegistryFileNotFoundError(
                f"Repository registry file not found: {self.path}"
            )

        if not self.path.is_file():
            raise RepositoryRegistryError(
                f"Repository registry path is not a file: {self.path}"
            )

        try:
            return yaml.safe_load(self.path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise RepositoryRegistryError(
                f"Failed to parse repository registry YAML: {exc}"
            ) from exc

    def _validate_registry_root(self, raw: Any) -> list[dict[str, Any]]:
        if raw is None:
            raw = {}

        if not isinstance(raw, dict):
            raise RepositoryRegistryError(
                f"Repository registry root must be a mapping, got {type(raw).__name__}"
            )

        repositories = raw.get("repositories")
        if repositories is None:
            raise RepositoryRegistryError(
                "Repository registry file must contain a 'repositories' list"
            )

        if not isinstance(repositories, list):
            raise RepositoryRegistryError(
                f"'repositories' must be a list, got {type(repositories).__name__}"
            )

        return repositories

    def _parse_repositories(
        self,
        repository_items: list[dict[str, Any]],
    ) -> list[Repository]:
        parsed: list[Repository] = []
        ids: set[str] = set()
        names: set[str] = set()

        for index, item in enumerate(repository_items):
            if not isinstance(item, dict):
                raise RepositoryRegistryError(
                    f"Repository entry at index {index} must be a mapping"
                )

            repository = Repository.from_dict(item)
            self._validate_repository(repository, index, ids, names)
            ids.add(repository.id)
            names.add(repository.name)
            parsed.append(repository)

        return parsed

    def _validate_repository(
        self,
        repository: Repository,
        index: int,
        ids: set[str],
        names: set[str],
    ) -> None:
        if not repository.id:
            raise MissingRepositoryFieldError(
                f"Repository entry at index {index} has an empty 'id'"
            )
        if not repository.name:
            raise MissingRepositoryFieldError(
                f"Repository entry at index {index} has an empty 'name'"
            )

        if repository.id in ids:
            raise DuplicateRepositoryIdError(
                f"Duplicate repository id found: {repository.id}"
            )
        if repository.name in names:
            raise DuplicateRepositoryNameError(
                f"Duplicate repository name found: {repository.name}"
            )
