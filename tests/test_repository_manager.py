from pathlib import Path
from textwrap import dedent

import pytest

from csgpt.repository import (
    DuplicateRepositoryIdError,
    DuplicateRepositoryNameError,
    MissingRepositoryFieldError,
    RepositoryManager,
    RepositoryRegistryFileNotFoundError,
    RepositoryRegistryError,
)


def test_load_registry_missing_file_raises(tmp_path: Path) -> None:
    manager = RepositoryManager(path=tmp_path / "missing.yaml")
    with pytest.raises(RepositoryRegistryFileNotFoundError):
        manager.load()


def test_load_registry_parses_repositories(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        dedent("""
            repositories:
              - id: cybersecgpt-cli
                name: CyberSecGPT CLI
                description: Command line interface
                category: core
                active: true
                path: cybersecgpt-cli
            """).strip() + "\n",
        encoding="utf-8",
    )
    manager = RepositoryManager(path=config_path)

    repos = manager.load()

    assert len(repos) == 1
    assert repos[0].id == "cybersecgpt-cli"
    assert repos[0].path == Path("cybersecgpt-cli")


def test_load_registry_duplicate_id_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        dedent("""
            repositories:
              - id: cybersecgpt-cli
                name: CyberSecGPT CLI
                description: Command line interface
                category: core
                active: true
                path: cybersecgpt-cli
              - id: cybersecgpt-cli
                name: CyberSecGPT CLI v2
                description: Duplicate id
                category: core
                active: true
                path: cybersecgpt-cli-v2
            """).strip() + "\n",
        encoding="utf-8",
    )
    manager = RepositoryManager(path=config_path)

    with pytest.raises(DuplicateRepositoryIdError):
        manager.load()


def test_load_registry_duplicate_name_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        dedent("""
            repositories:
              - id: cybersecgpt-cli
                name: CyberSecGPT CLI
                description: Command line interface
                category: core
                active: true
                path: cybersecgpt-cli
              - id: cybersecgpt-cli-v2
                name: CyberSecGPT CLI
                description: Duplicate name
                category: core
                active: true
                path: cybersecgpt-cli-v2
            """).strip() + "\n",
        encoding="utf-8",
    )
    manager = RepositoryManager(path=config_path)

    with pytest.raises(DuplicateRepositoryNameError):
        manager.load()


def test_load_registry_missing_field_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        dedent("""
            repositories:
              - id: cybersecgpt-cli
                name: CyberSecGPT CLI
                category: core
                active: true
                path: cybersecgpt-cli
            """).strip() + "\n",
        encoding="utf-8",
    )
    manager = RepositoryManager(path=config_path)

    with pytest.raises(MissingRepositoryFieldError):
        manager.load()


def test_load_registry_invalid_root_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text("- invalid: root", encoding="utf-8")
    manager = RepositoryManager(path=config_path)

    with pytest.raises(RepositoryRegistryError):
        manager.load()


def test_load_registry_invalid_yaml_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        """
        repositories:
          - id: cybersecgpt-cli
            name: CyberSecGPT CLI
            description: [unclosed
        """.strip() + "\n",
        encoding="utf-8",
    )
    manager = RepositoryManager(path=config_path)

    with pytest.raises(RepositoryRegistryError):
        manager.load()


def test_load_registry_empty_returns_no_repositories(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text("repositories: []\n", encoding="utf-8")
    manager = RepositoryManager(path=config_path)

    repos = manager.load()
    assert repos == []
