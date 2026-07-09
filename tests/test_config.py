from pathlib import Path
from textwrap import dedent

import pytest

from csgpt.config import (
    ConfigurationError,
    ConfigurationFileNotFoundError,
    ConfigurationManager,
)


def test_load_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"
    with pytest.raises(ConfigurationFileNotFoundError):
        ConfigurationManager.load(missing)


def test_load_defaults_and_show_as_dict(tmp_path: Path) -> None:
    config_path = tmp_path / "bootstrap.yaml"
    config_path.write_text(
        dedent("""
            bootstrap:
              project_name: test-project
            paths:
              source: src/
            settings:
              enable_diagnostics: false
              default_branch: develop
            """).strip() + "\n",
        encoding="utf-8",
    )

    manager = ConfigurationManager.load(config_path)
    assert manager.path == config_path
    data = manager.as_dict()
    assert data["bootstrap"]["project_name"] == "test-project"
    assert data["paths"]["source"] == "src/"
    assert data["settings"]["default_branch"] == "develop"
    assert data["bootstrap"]["author"] == "cybsec-ops"


def test_load_invalid_yaml_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "bootstrap.yaml"
    config_path.write_text("not: [valid", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        ConfigurationManager.load(config_path)


def test_load_invalid_section_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "bootstrap.yaml"
    config_path.write_text("bootstrap: 123", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        ConfigurationManager.load(config_path)
