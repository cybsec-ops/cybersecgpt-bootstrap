"""Minimal CLI for CyberSecGPT Bootstrap.

Provides a `csgpt` console entry point with help text.
"""
from __future__ import annotations

import argparse
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns:
        argparse.ArgumentParser: configured parser
    """
    parser = argparse.ArgumentParser(prog="csgpt", description="CyberSecGPT Bootstrap CLI")
    parser.add_argument("--version", action="version", version="csgpt 0.1.0")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint.

    This function is used as the console script entry in `pyproject.toml`.
    It only parses arguments and prints help/version; no business logic is executed.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # configure basic logging
    logging.basicConfig(level=logging.INFO)
    logger.info("csgpt invoked with args: %s", args)

    # No further action for scaffold
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
