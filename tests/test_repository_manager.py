from pathlib import Path

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
        """repositories:\n  - id: cybersecgpt-cli\n    name: CyberSecGPT CLI\n    description: Command line interface\n    category: core\n    active: true\n    path: cybersecgpt-cli\n""",
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
        """repositories:\n  - id: cybersecgpt-cli\n    name: CyberSecGPT CLI\n    description: Command line interface\n    category: core\n    active: true\n    path: cybersecgpt-cli\n  - id: cybersecgpt-cli\n    name: CyberSecGPT CLI v2\n    description: Duplicate id\n    category: core\n    active: true\n    path: cybersecgpt-cli-v2\n""",
        encoding="utf-8",
    )
    manager = RepositoryManager(path=config_path)

    with pytest.raises(DuplicateRepositoryIdError):
        manager.load()


def test_load_registry_duplicate_name_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        """repositories:\n  - id: cybersecgpt-cli\n    name: CyberSecGPT CLI\n    description: Command line interface\n    category: core\n    active: true\n    path: cybersecgpt-cli\n  - id: cybersecgpt-cli-v2\n    name: CyberSecGPT CLI\n    description: Duplicate name\n    category: core\n    active: true\n    path: cybersecgpt-cli-v2\n""",
        encoding="utf-8",
    )
    manager = RepositoryManager(path=config_path)

    with pytest.raises(DuplicateRepositoryNameError):
        manager.load()


def test_load_registry_missing_field_raises(tmp_path: Path) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        """repositories:\n  - id: cybersecgpt-cli\n    name: CyberSecGPT CLI\n    category: core\n    active: true\n    path: cybersecgpt-cli\n""",
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
        "repositories:\n  - id: cybersecgpt-cli\n    name: CyberSecGPT CLI\n    description: [unclosed\n",
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
