"""Server configuration resolved from environment with sane defaults."""

from __future__ import annotations

import os

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 6379


def host() -> str:
    """Bind host, overridable via the ``SNAKE_DB_HOST`` environment variable."""
    return os.environ.get("SNAKE_DB_HOST", DEFAULT_HOST)


def port() -> int:
    """Bind port, overridable via the ``SNAKE_DB_PORT`` environment variable."""
    return int(os.environ.get("SNAKE_DB_PORT", DEFAULT_PORT))


def verbose() -> bool:
    """Whether to log per-client connect/disconnect (off by default to keep
    test and server output quiet). Enable with ``SNAKE_DB_VERBOSE=1``."""
    return os.environ.get("SNAKE_DB_VERBOSE") == "1"
