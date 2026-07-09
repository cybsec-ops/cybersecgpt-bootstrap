import subprocess
from pathlib import Path

import pytest

from csgpt.doctor import DoctorService


def test_doctor_resolves_repository_paths_against_workspace_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace_root = tmp_path / "workspace-root"
    workspace_root.mkdir()

    repo_dir = workspace_root / "cybersecgpt-bootstrap"
    repo_dir.mkdir()

    workspace = tmp_path / "workspace-config"
    workspace.mkdir()
    bootstrap = workspace / "configs" / "bootstrap.yaml"
    registry = workspace / "configs" / "repositories.yaml"
    bootstrap.parent.mkdir(parents=True, exist_ok=True)
    registry.parent.mkdir(parents=True, exist_ok=True)

    bootstrap.write_text(
        "bootstrap:\n  project_name: test\nworkspace:\n  root: {}\n".format(
            workspace_root.as_posix()
        ),
        encoding="utf-8",
    )
    registry.write_text(
        "repositories:\n  - id: cybersecgpt-bootstrap\n    name: CyberSecGPT Bootstrap\n    description: Bootstrap repository\n    category: tooling\n    active: true\n    path: cybersecgpt-bootstrap\n",
        encoding="utf-8",
    )

    monkeypatch.setattr("csgpt.doctor.shutil.which", lambda name: f"/usr/bin/{name}")

    def fake_run(command, capture_output, text, check):
        if command[:2] == ["/usr/bin/git", "--version"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="git version 2.40.0\n", stderr=""
            )
        if command[:3] == ["/usr/bin/gh", "auth", "status"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="github.com: Logged in as user\n", stderr=""
            )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(
        "csgpt.doctor.DoctorService._run_command",
        lambda self, command, check=False: fake_run(
            command, capture_output=True, text=True, check=check
        ),
    )

    service = DoctorService(workspace=workspace)
    exit_code = service.run(json_output=True)

    assert exit_code == 0
