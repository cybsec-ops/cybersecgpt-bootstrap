"""CyberSecGPT Bootstrap CLI.

This module provides the full command tree for the CLI without implementing
business logic.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from pprint import pprint
from typing import Optional

from csgpt.config import ConfigurationError, ConfigurationManager
from csgpt.doctor import DoctorService
from csgpt.repository import RepositoryManager, RepositoryRegistryError

logger = logging.getLogger(__name__)


def _handle_init(args: argparse.Namespace) -> int:
    logger.info("Running init command with args=%s", args)
    return 0


def _handle_repo_create(args: argparse.Namespace) -> int:
    logger.info("Running repo create with args=%s", args)
    return 0


def _handle_repo_clone(args: argparse.Namespace) -> int:
    logger.info("Running repo clone with args=%s", args)
    return 0


def _handle_repo_sync(args: argparse.Namespace) -> int:
    logger.info("Running repo sync with args=%s", args)
    return 0


def _handle_repo_list(args: argparse.Namespace) -> int:
    logger.info("Running repo list with args=%s", args)

    try:
        manager = RepositoryManager(path=getattr(args, "registry_path", None))
        repositories = manager.load()
    except RepositoryRegistryError as exc:
        logger.error("Repository list failed: %s", exc)
        print(f"Repository registry error: {exc}")
        return 1

    repositories = sorted(repositories, key=lambda repo: repo.id.lower())
    headers = ["ID", "Name", "Category", "Active", "Local Path"]
    rows = [
        (
            repo.id,
            repo.name,
            repo.category,
            "Yes" if repo.active else "No",
            str(repo.path),
        )
        for repo in repositories
    ]

    if not rows:
        print("No repositories found.")
        return 0

    widths = [
        max(len(header), max(len(row[idx]) for row in rows))
        for idx, header in enumerate(headers)
    ]
    header_row = "  ".join(
        header.ljust(widths[idx]) for idx, header in enumerate(headers)
    )
    separator = "  ".join("-" * widths[idx] for idx in range(len(headers)))

    print(header_row)
    print(separator)
    for row in rows:
        print("  ".join(str(value).ljust(widths[idx]) for idx, value in enumerate(row)))

    return 0


def _handle_repo_status(args: argparse.Namespace) -> int:
    logger.info("Running repo status with args=%s", args)
    return 0


def _handle_docs_generate(args: argparse.Namespace) -> int:
    logger.info("Running docs generate with args=%s", args)
    return 0


def _handle_docs_build(args: argparse.Namespace) -> int:
    logger.info("Running docs build with args=%s", args)
    return 0


def _handle_docs_validate(args: argparse.Namespace) -> int:
    logger.info("Running docs validate with args=%s", args)
    return 0


def _handle_template_apply(args: argparse.Namespace) -> int:
    logger.info("Running template apply with args=%s", args)
    return 0


def _handle_template_update(args: argparse.Namespace) -> int:
    logger.info("Running template update with args=%s", args)
    return 0


def _handle_template_list(args: argparse.Namespace) -> int:
    logger.info("Running template list with args=%s", args)
    return 0


def _handle_config_init(args: argparse.Namespace) -> int:
    logger.info("Running config init with args=%s", args)
    return 0


def _handle_config_validate(args: argparse.Namespace) -> int:
    logger.info("Running config validate with args=%s", args)
    try:
        ConfigurationManager.load(args.path)
    except ConfigurationError as exc:
        logger.error("Configuration validation failed: %s", exc)
        print(f"Configuration validation failed: {exc}")
        return 1

    print(f"Configuration at {args.path} is valid.")
    return 0


def _handle_config_show(args: argparse.Namespace) -> int:
    logger.info("Running config show with args=%s", args)
    try:
        manager = ConfigurationManager.load(args.path)
    except ConfigurationError as exc:
        logger.error("Configuration loading failed: %s", exc)
        print(f"Configuration loading failed: {exc}")
        return 1

    pprint(manager.as_dict())
    return 0


def _handle_doctor(args: argparse.Namespace) -> int:
    logger.info("Running doctor command with args=%s", args)
    service = DoctorService(
        workspace=(
            args.workspace if getattr(args, "workspace", None) is not None else None
        ),
        bootstrap_path=(
            args.bootstrap_path
            if getattr(args, "bootstrap_path", None) is not None
            else None
        ),
        registry_path=(
            args.registry_path
            if getattr(args, "registry_path", None) is not None
            else None
        ),
        verbose=args.verbose,
    )
    return service.run(json_output=args.json)


def _handle_version(args: argparse.Namespace) -> int:
    logger.info("Running version command")
    print("csgpt version 0.1.0")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="csgpt", description="CyberSecGPT Bootstrap CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "init", help="Initialize a new CyberSecGPT project"
    ).set_defaults(func=_handle_init)

    repo_parser = subparsers.add_parser("repo", help="Manage repositories")
    repo_subparsers = repo_parser.add_subparsers(dest="repo_command", required=True)
    repo_create = repo_subparsers.add_parser("create", help="Create a repository")
    repo_create.add_argument("name", help="Repository name")
    repo_create.set_defaults(func=_handle_repo_create)

    repo_clone = repo_subparsers.add_parser("clone", help="Clone a repository")
    repo_clone.add_argument("url", help="Repository URL")
    repo_clone.add_argument(
        "--path", type=Path, default=Path.cwd(), help="Destination path"
    )
    repo_clone.set_defaults(func=_handle_repo_clone)

    repo_sync = repo_subparsers.add_parser("sync", help="Sync a repository")
    repo_sync.add_argument("name", help="Repository name")
    repo_sync.set_defaults(func=_handle_repo_sync)

    repo_list = repo_subparsers.add_parser("list", help="List repositories")
    repo_list.add_argument(
        "--registry-path",
        type=Path,
        default=Path("configs/repositories.yaml"),
        help="Path to the repository registry YAML file",
    )
    repo_list.set_defaults(func=_handle_repo_list)

    repo_status = repo_subparsers.add_parser("status", help="Show repository status")
    repo_status.add_argument("name", help="Repository name")
    repo_status.set_defaults(func=_handle_repo_status)

    docs_parser = subparsers.add_parser("docs", help="Manage documentation")
    docs_subparsers = docs_parser.add_subparsers(dest="docs_command", required=True)
    docs_generate = docs_subparsers.add_parser(
        "generate", help="Generate documentation"
    )
    docs_generate.add_argument(
        "--output", type=Path, default=Path("docs"), help="Output directory"
    )
    docs_generate.set_defaults(func=_handle_docs_generate)

    docs_build = docs_subparsers.add_parser("build", help="Build documentation")
    docs_build.add_argument(
        "--output", type=Path, default=Path("site"), help="Build directory"
    )
    docs_build.set_defaults(func=_handle_docs_build)

    docs_validate = docs_subparsers.add_parser(
        "validate", help="Validate documentation"
    )
    docs_validate.set_defaults(func=_handle_docs_validate)

    template_parser = subparsers.add_parser("template", help="Manage templates")
    template_subparsers = template_parser.add_subparsers(
        dest="template_command", required=True
    )
    template_apply = template_subparsers.add_parser("apply", help="Apply a template")
    template_apply.add_argument("name", help="Template name")
    template_apply.add_argument(
        "--destination", type=Path, default=Path.cwd(), help="Destination directory"
    )
    template_apply.set_defaults(func=_handle_template_apply)

    template_update = template_subparsers.add_parser("update", help="Update templates")
    template_update.add_argument("name", help="Template name")
    template_update.set_defaults(func=_handle_template_update)

    template_list = template_subparsers.add_parser("list", help="List templates")
    template_list.set_defaults(func=_handle_template_list)

    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(
        dest="config_command", required=True
    )
    config_init = config_subparsers.add_parser("init", help="Initialize configuration")
    config_init.add_argument(
        "--path",
        type=Path,
        default=Path("configs/bootstrap.yaml"),
        help="Configuration file path",
    )
    config_init.set_defaults(func=_handle_config_init)

    config_validate = config_subparsers.add_parser(
        "validate", help="Validate configuration"
    )
    config_validate.add_argument(
        "--path",
        type=Path,
        default=Path("configs/bootstrap.yaml"),
        help="Configuration file path",
    )
    config_validate.set_defaults(func=_handle_config_validate)

    config_show = config_subparsers.add_parser("show", help="Show configuration")
    config_show.add_argument(
        "--path",
        type=Path,
        default=Path("configs/bootstrap.yaml"),
        help="Configuration file path",
    )
    config_show.set_defaults(func=_handle_config_show)

    doctor_parser = subparsers.add_parser("doctor", help="Run CLI diagnostics")
    doctor_parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root directory",
    )
    doctor_parser.add_argument(
        "--bootstrap-path",
        type=Path,
        default=Path("configs/bootstrap.yaml"),
        help="Bootstrap configuration file path relative to workspace",
    )
    doctor_parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path("configs/repositories.yaml"),
        help="Repository registry file path relative to workspace",
    )
    doctor_parser.add_argument(
        "--json",
        action="store_true",
        help="Output the doctor report as JSON",
    )
    doctor_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging for the doctor command",
    )
    doctor_parser.set_defaults(func=_handle_doctor)

    version_parser = subparsers.add_parser("version", help="Show CLI version")
    version_parser.set_defaults(func=_handle_version)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint.

    Parses arguments and dispatches to placeholder handlers.
    """
    logging.basicConfig(level=logging.INFO)
    parser = build_parser()
    args = parser.parse_args(argv)

    logger.info("csgpt invoked with args=%s", args)
    result = getattr(args, "func", None)
    if result is None:
        parser.print_help()
        return 1
    return result(args)


if __name__ == "__main__":
    raise SystemExit(main())
