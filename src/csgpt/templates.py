"""Template utilities for discovering, validating, and rendering project templates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


@dataclass
class TemplateManager:
    """Manage project templates.

    Attributes:
        templates_dir: Path
    """

    templates_dir: Path

    _PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")
    _SUPPORTED_PLACEHOLDERS = {
        "project_name",
        "package_name",
        "author",
        "organization",
        "description",
        "version",
        "repository_url",
        "license",
    }

    def list(self) -> list[str]:
        """List available template directories in the template library."""
        if not self.templates_dir.exists():
            return []
        if not self.templates_dir.is_dir():
            raise NotADirectoryError(
                f"Template directory is not a directory: {self.templates_dir}"
            )

        return sorted(
            path.name
            for path in self.templates_dir.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        )

    def validate(self, name: str) -> bool:
        """Validate that a template directory contains required content."""
        template_path = self.templates_dir / name
        if not template_path.exists():
            raise ValueError(f"Template not found: {name}")
        if not template_path.is_dir():
            raise ValueError(f"Template path is not a directory: {template_path}")

        has_files = False
        for path in template_path.rglob("*"):
            if path.is_dir():
                continue

            has_files = True
            if self._has_invalid_filename(path.name):
                raise ValueError(f"Invalid filename in template: {path.name}")
            self._validate_placeholder_syntax(path)

        return has_files

    def render(
        self,
        name: str,
        destination: Path,
        replacements: dict[str, str] | None = None,
    ) -> None:
        """Render a template directory to the requested destination path."""
        template_path = self.templates_dir / name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {name}")
        if not template_path.is_dir():
            raise NotADirectoryError(f"Template path is not a directory: {template_path}")

        replacements = self._normalize_replacements(replacements)
        destination_path = destination.expanduser()
        destination_path.mkdir(parents=True, exist_ok=True)

        files = sorted(template_path.rglob("*"))
        for source_path in files:
            if source_path.is_dir():
                continue

            relative_path = source_path.relative_to(template_path)
            target_path = destination_path / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)

            content = source_path.read_text(encoding="utf-8")
            substituted = self._substitute_placeholders(content, replacements)
            if self._PLACEHOLDER_PATTERN.search(substituted):
                raise ValueError(
                    f"Unresolved placeholders detected in {source_path.relative_to(template_path)}"
                )

            target_path.write_text(substituted, encoding="utf-8")

        return None

    def _normalize_replacements(self, replacements: dict[str, str] | None) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for placeholder, value in (replacements or {}).items():
            if placeholder not in self._SUPPORTED_PLACEHOLDERS:
                raise ValueError(f"Unsupported placeholder: {placeholder}")
            normalized[placeholder] = str(value)

        missing_defaults = self._SUPPORTED_PLACEHOLDERS - normalized.keys()
        for placeholder in missing_defaults:
            normalized.setdefault(placeholder, "")

        project_name = normalized.get("project_name", "").strip()
        package_name = normalized.get("package_name", "").strip()
        if package_name:
            normalized["package_name"] = self._slugify_package_name(package_name)
        elif project_name:
            normalized["package_name"] = self._slugify_package_name(project_name)

        self._validate_replacement_values(normalized)
        return normalized

    def _validate_replacement_values(self, replacements: dict[str, str]) -> None:
        if not replacements.get("project_name"):
            raise ValueError("project_name replacement is required")
        if not replacements.get("package_name"):
            raise ValueError("package_name replacement is required")

    @staticmethod
    def _slugify_package_name(value: str) -> str:
        slug = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_").lower()
        return slug or "project"

    def _substitute_placeholders(self, content: str, replacements: dict[str, str]) -> str:
        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in replacements:
                raise ValueError(f"Missing replacement for placeholder: {{{{{key}}}}}")
            return replacements[key]

        return self._PLACEHOLDER_PATTERN.sub(replace, content)

    def _validate_placeholder_syntax(self, path: Path) -> None:
        content = path.read_text(encoding="utf-8")
        placeholders = self._PLACEHOLDER_PATTERN.findall(content)
        if not placeholders:
            return

        if len(placeholders) != len(set(placeholders)):
            raise ValueError(f"Duplicate placeholders detected in {path.name}")

        unsupported = [name for name in placeholders if name not in self._SUPPORTED_PLACEHOLDERS]
        if unsupported:
            raise ValueError(f"Unsupported placeholders in {path.name}: {unsupported}")

    def _has_invalid_filename(self, filename: str) -> bool:
        invalid_segments = ["..", "/", "\\"]
        return any(segment in filename for segment in invalid_segments)
