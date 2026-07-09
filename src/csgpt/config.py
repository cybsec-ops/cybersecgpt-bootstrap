"""Configuration management for CyberSecGPT Bootstrap."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """Raised when configuration is invalid or cannot be loaded."""


class ConfigurationFileNotFoundError(ConfigurationError):
    """Raised when the expected configuration file does not exist."""


@dataclass
class ConfigurationManager:
    """Loads and validates the bootstrap configuration."""

    path: Path
    config: dict[str, Any] = field(default_factory=dict)

    DEFAULT_PATH = Path("configs/bootstrap.yaml")

    @classmethod
    def load(cls, path: Path | None = None) -> "ConfigurationManager":
        """Load configuration from a YAML file and validate its contents."""
        config_path = (path or cls.DEFAULT_PATH).expanduser()

        if not config_path.exists():
            raise ConfigurationFileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        if not config_path.is_file():
            raise ConfigurationError(f"Configuration path is not a file: {config_path}")

        try:
            with config_path.open("r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise ConfigurationError(f"Failed to parse YAML file: {exc}") from exc

        if raw is None:
            raw = {}

        if not isinstance(raw, dict):
            raise ConfigurationError(
                f"Configuration root must be a mapping, got {type(raw).__name__}"
            )

        manager = cls(path=config_path, config=raw)
        manager._apply_defaults()
        manager._validate()
        return manager

    def _apply_defaults(self) -> None:
        """Apply default values for missing configuration sections."""
        bootstrap_section = self.config.setdefault("bootstrap", {})
        if bootstrap_section is None or not isinstance(bootstrap_section, dict):
            raise ConfigurationError("Configuration 'bootstrap' section must be a mapping.")

        bootstrap_section.setdefault("project_name", "cybersecgpt-bootstrap")
        bootstrap_section.setdefault("version", "0.1.0")
        bootstrap_section.setdefault("author", "cybsec-ops")
        bootstrap_section.setdefault(
            "description",
            "CyberSecGPT bootstrap project configuration",
        )

        paths_section = self.config.setdefault("paths", {})
        if paths_section is None or not isinstance(paths_section, dict):
            raise ConfigurationError("Configuration 'paths' section must be a mapping.")

        paths_section.setdefault("source", "src/")
        paths_section.setdefault("docs", "docs/")
        paths_section.setdefault("config", "configs/")
        paths_section.setdefault("templates", "templates/")

        settings_section = self.config.setdefault("settings", {})
        if settings_section is None or not isinstance(settings_section, dict):
            raise ConfigurationError("Configuration 'settings' section must be a mapping.")

        settings_section.setdefault("enable_diagnostics", True)
        settings_section.setdefault("default_branch", "main")

    def _validate(self) -> None:
        """Validate loaded configuration values."""
        if not self.config["bootstrap"].get("project_name"):
            raise ConfigurationError("bootstrap.project_name must be set.")

        if not isinstance(self.config["settings"]["enable_diagnostics"], bool):
            raise ConfigurationError("settings.enable_diagnostics must be a boolean.")

        if not isinstance(self.config["settings"]["default_branch"], str):
            raise ConfigurationError("settings.default_branch must be a string.")

    def as_dict(self) -> dict[str, Any]:
        """Return the loaded configuration as a dictionary."""
        return dict(self.config)
