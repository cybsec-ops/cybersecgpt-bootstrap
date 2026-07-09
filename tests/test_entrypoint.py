import importlib
import sys
from pathlib import Path

import pytest

from csgpt import cli


def test_cli_help_prints_and_exits(capsys) -> None:
    parser = cli.build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])
    # argparse raises SystemExit with code 0 for --help
    assert excinfo.value.code in (None, 0)


def test_package_modules_exist() -> None:
    package = importlib.import_module("csgpt")
    # Ensure key modules are importable
    for mod in ("cli", "bootstrap", "repository", "github", "templates", "config", "utils"):
        fullname = f"csgpt.{mod}"
        m = importlib.import_module(fullname)
        assert m is not None


def test_project_structure_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "pyproject.toml").exists()
    assert (root / "src").is_dir()
    assert (root / "tests").is_dir()
