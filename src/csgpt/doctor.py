"""Doctor command support for CyberSecGPT Bootstrap."""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml

from csgpt.repository import RepositoryManager, RepositoryRegistryError

logger = logging.getLogger(__name__)


@dataclass
class DoctorCheckResult:
    """Result of a single diagnostic check."""

    status: str
    check: str
    value: str
    details: str = ""
    critical: bool = True


class DoctorService:
    """Runs environment and workspace diagnostic checks."""

    def __init__(
        self,
        workspace: Path | None = None,
        bootstrap_path: Path | None = None,
        registry_path: Path | None = None,
        verbose: bool = False,
    ) -> None:
        self.work_dir = (workspace or Path.cwd()).expanduser().resolve()
        self.bootstrap_path = (
            bootstrap_path or Path("configs/bootstrap.yaml")
        ).expanduser()
        self.registry_path = (
            registry_path or Path("configs/repositories.yaml")
        ).expanduser()
        self.verbose = verbose
        self.workspace_root: Path | None = None

        if self.verbose:
            logging.basicConfig(level=logging.DEBUG)

    def run(self, json_output: bool = False) -> int:
        """Run all checks and render the doctor report."""
        results = self.run_checks()
        all_required_passed = all(
            result.status == "PASS" for result in results if result.critical
        )

        if json_output:
            print(json.dumps([asdict(result) for result in results], indent=2))
        else:
            self._display_table(results)

        return 0 if all_required_passed else 1

    def run_checks(self) -> list[DoctorCheckResult]:
        """Run all configured diagnostic checks."""
        results: list[DoctorCheckResult] = []

        results.append(self._check_python_executable())
        results.append(self._check_python_version())
        results.append(self._check_git_executable())
        results.append(self._check_git_version())
        results.append(self._check_github_cli_executable())
        results.append(self._check_github_authentication())
        results.append(self._check_workspace_config())
        results.append(self._check_bootstrap_config_exists())
        results.append(self._check_repository_registry_exists())
        results.append(self._check_configured_repositories())
        results.append(self._check_repository_directories())
        results.append(self._check_operating_system())
        results.append(self._check_current_working_directory())
        results.append(self._check_writable_workspace())

        return results

    def _check_python_executable(self) -> DoctorCheckResult:
        executable = (
            shutil.which("python") or shutil.which("python3") or shutil.which("py")
        )
        if executable:
            return DoctorCheckResult(
                status="PASS",
                check="Python executable",
                value=executable,
            )

        return DoctorCheckResult(
            status="FAIL",
            check="Python executable",
            value="Not found",
            details="Python executable is not available on PATH.",
        )

    def _check_python_version(self) -> DoctorCheckResult:
        version = platform.python_version()
        return DoctorCheckResult(
            status="PASS",
            check="Python version",
            value=version,
        )

    def _check_git_executable(self) -> DoctorCheckResult:
        executable = shutil.which("git")
        if executable:
            return DoctorCheckResult(
                status="PASS",
                check="Git executable",
                value=executable,
            )

        return DoctorCheckResult(
            status="FAIL",
            check="Git executable",
            value="Not found",
            details="Git must be installed and available on PATH.",
        )

    def _check_git_version(self) -> DoctorCheckResult:
        executable = shutil.which("git")
        if not executable:
            return DoctorCheckResult(
                status="FAIL",
                check="Git version",
                value="Unavailable",
                details="Git executable not found.",
            )

        result = self._run_command([executable, "--version"])
        if result.returncode == 0:
            return DoctorCheckResult(
                status="PASS",
                check="Git version",
                value=result.stdout.strip(),
            )

        return DoctorCheckResult(
            status="FAIL",
            check="Git version",
            value="Failed",
            details=result.stderr.strip() or "Unable to determine Git version.",
        )

    def _check_github_cli_executable(self) -> DoctorCheckResult:
        executable = shutil.which("gh")
        if executable:
            return DoctorCheckResult(
                status="PASS",
                check="GitHub CLI executable",
                value=executable,
            )

        return DoctorCheckResult(
            status="FAIL",
            check="GitHub CLI executable",
            value="Not found",
            details="GitHub CLI must be installed and available on PATH.",
        )

    def _check_github_authentication(self) -> DoctorCheckResult:
        executable = shutil.which("gh")
        if not executable:
            return DoctorCheckResult(
                status="FAIL",
                check="GitHub authentication",
                value="Unavailable",
                details="GitHub CLI executable not found.",
            )

        result = self._run_command([executable, "auth", "status"], check=False)
        if result.returncode == 0:
            return DoctorCheckResult(
                status="PASS",
                check="GitHub authentication",
                value="Authenticated",
                details=result.stdout.strip().splitlines()[0] if result.stdout else "",
            )

        return DoctorCheckResult(
            status="FAIL",
            check="GitHub authentication",
            value="Not authenticated",
            details=result.stderr.strip()
            or result.stdout.strip()
            or "gh auth status failed.",
        )

    def _check_workspace_config(self) -> DoctorCheckResult:
        config_path = self.work_dir / self.bootstrap_path
        if not config_path.exists() or not config_path.is_file():
            return DoctorCheckResult(
                status="FAIL",
                check="Bootstrap configuration",
                value=str(config_path),
                details="Bootstrap config file is missing or invalid.",
            )

        try:
            with config_path.open("r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            return DoctorCheckResult(
                status="FAIL",
                check="Bootstrap configuration",
                value=str(config_path),
                details=f"Failed to parse YAML: {exc}",
            )

        if not isinstance(raw, dict):
            return DoctorCheckResult(
                status="FAIL",
                check="Bootstrap configuration",
                value=str(config_path),
                details="Bootstrap config root must be a mapping.",
            )

        bootstrap = raw.get("bootstrap")
        if not isinstance(bootstrap, dict):
            return DoctorCheckResult(
                status="FAIL",
                check="Bootstrap configuration",
                value=str(config_path),
                details="Missing 'bootstrap' section in config.",
            )

        workspace_root_value = (
            raw.get("workspace", {}).get("root")
            if isinstance(raw.get("workspace"), dict)
            else None
        )
        if (
            not isinstance(workspace_root_value, str)
            or not workspace_root_value.strip()
        ):
            return DoctorCheckResult(
                status="FAIL",
                check="Workspace root",
                value=str(config_path),
                details="Missing or invalid workspace.root in bootstrap config.",
            )

        self.workspace_root = (Path(workspace_root_value).expanduser()).resolve()
        if not self.workspace_root.exists() or not self.workspace_root.is_dir():
            return DoctorCheckResult(
                status="FAIL",
                check="Workspace root",
                value=str(self.workspace_root),
                details="Resolved workspace.root does not exist.",
            )

        return DoctorCheckResult(
            status="PASS",
            check="Workspace root",
            value=str(self.workspace_root),
            details="Workspace root resolved from bootstrap config.",
        )

    def _check_bootstrap_config_exists(self) -> DoctorCheckResult:
        path = self.work_dir / self.bootstrap_path
        if path.exists() and path.is_file():
            return DoctorCheckResult(
                status="PASS",
                check="Bootstrap config exists",
                value=str(path),
            )

        return DoctorCheckResult(
            status="FAIL",
            check="Bootstrap config exists",
            value=str(path),
            details="Bootstrap configuration file is missing.",
        )

    def _check_repository_registry_exists(self) -> DoctorCheckResult:
        path = self.work_dir / self.registry_path
        if path.exists() and path.is_file():
            return DoctorCheckResult(
                status="PASS",
                check="Repository registry exists",
                value=str(path),
            )

        return DoctorCheckResult(
            status="FAIL",
            check="Repository registry exists",
            value=str(path),
            details="Repository registry file is missing.",
        )

    def _check_configured_repositories(self) -> DoctorCheckResult:
        path = self.work_dir / self.registry_path
        if not path.exists() or not path.is_file():
            return DoctorCheckResult(
                status="FAIL",
                check="Configured repositories",
                value="Unavailable",
                details="Repository registry not available.",
            )

        try:
            manager = RepositoryManager(path=path)
            repositories = manager.load()
        except RepositoryRegistryError as exc:
            return DoctorCheckResult(
                status="FAIL",
                check="Configured repositories",
                value="Invalid registry",
                details=str(exc),
            )

        return DoctorCheckResult(
            status="PASS",
            check="Configured repositories",
            value=str(len(repositories)),
            details="Repository registry loaded successfully.",
        )

    def _check_repository_directories(self) -> DoctorCheckResult:
        if self.workspace_root is None:
            return DoctorCheckResult(
                status="FAIL",
                check="Repository directories",
                value="Unavailable",
                details="Workspace root has not been resolved.",
            )

        registry_path = self.work_dir / self.registry_path
        if not registry_path.exists() or not registry_path.is_file():
            return DoctorCheckResult(
                status="FAIL",
                check="Repository directories",
                value="Unavailable",
                details="Repository registry not available.",
            )

        try:
            manager = RepositoryManager(path=registry_path)
            repositories = manager.load()
        except RepositoryRegistryError as exc:
            return DoctorCheckResult(
                status="FAIL",
                check="Repository directories",
                value="Invalid registry",
                details=str(exc),
            )

        missing = [
            repo.id
            for repo in repositories
            if not (self.workspace_root / repo.path).resolve().exists()
        ]
        if missing:
            return DoctorCheckResult(
                status="FAIL",
                check="Repository directories",
                value=str(len(repositories)),
                details=f"Missing directories: {', '.join(missing)}",
            )

        return DoctorCheckResult(
            status="PASS",
            check="Repository directories",
            value=str(len(repositories)),
            details="All repository directories exist.",
        )

    def _check_operating_system(self) -> DoctorCheckResult:
        value = platform.platform()
        return DoctorCheckResult(
            status="PASS",
            check="Operating system",
            value=value,
        )

    def _check_current_working_directory(self) -> DoctorCheckResult:
        return DoctorCheckResult(
            status="PASS",
            check="Workspace configuration directory",
            value=str(self.work_dir),
        )

    def _check_writable_workspace(self) -> DoctorCheckResult:
        target = self.workspace_root or self.work_dir
        try:
            writable = os.access(target, os.W_OK)
            if writable:
                return DoctorCheckResult(
                    status="PASS",
                    check="Writable workspace",
                    value=str(target),
                )

            return DoctorCheckResult(
                status="FAIL",
                check="Writable workspace",
                value=str(target),
                details="Workspace is not writable.",
            )
        except Exception as exc:
            return DoctorCheckResult(
                status="FAIL",
                check="Writable workspace",
                value=str(target),
                details=str(exc),
            )

    def _display_table(self, results: list[DoctorCheckResult]) -> None:
        headers = ["Status", "Check", "Value", "Details"]
        rows = [
            (result.status, result.check, result.value, result.details or "")
            for result in results
        ]
        widths = [
            max(len(headers[idx]), max(len(str(row[idx])) for row in rows))
            for idx in range(len(headers))
        ]
        header_row = "  ".join(
            headers[idx].ljust(widths[idx]) for idx in range(len(headers))
        )
        separator = "  ".join("-" * widths[idx] for idx in range(len(headers)))

        print(header_row)
        print(separator)
        for row in rows:
            print(
                "  ".join(
                    str(value).ljust(widths[idx]) for idx, value in enumerate(row)
                )
            )

    def _run_command(
        self, command: list[str], check: bool = False
    ) -> subprocess.CompletedProcess[Any]:
        logger.debug("Running command: %s", command)
        try:
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check,
            )
        except Exception as exc:
            logger.debug("Command failed: %s", exc)
            return subprocess.CompletedProcess(command, 1, stdout="", stderr=str(exc))
