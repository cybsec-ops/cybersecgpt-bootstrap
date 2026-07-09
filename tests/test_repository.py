from pathlib import Path

from csgpt.repository import Repository


def test_repository_dataclass_fields() -> None:
    repo = Repository(
        id="cybersecgpt-cli",
        name="CyberSecGPT CLI",
        description="Command line interface for CyberSecGPT utilities.",
        category="core",
        active=True,
        path=Path("cybersecgpt-cli"),
    )

    assert repo.id == "cybersecgpt-cli"
    assert repo.name == "CyberSecGPT CLI"
    assert repo.description == "Command line interface for CyberSecGPT utilities."
    assert repo.category == "core"
    assert repo.active is True
    assert repo.path == Path("cybersecgpt-cli")
