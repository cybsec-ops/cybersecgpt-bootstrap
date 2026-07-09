"""csgpt package - CyberSecGPT Bootstrap.

Lightweight package metadata and exports.
"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cybersecgpt-bootstrap")
except PackageNotFoundError:  # pragma: no cover - packaging time
    __version__ = "0.0.0"

__all__ = ["cli", "bootstrap", "repository", "github", "templates", "config", "utils"]
