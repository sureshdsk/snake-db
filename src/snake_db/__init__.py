"""snake-db: a minimal RESP2 Redis-compatible server built from scratch."""

from __future__ import annotations

from .server import serve

__all__ = ["serve", "main", "__version__"]
__version__ = "0.1.0"


def main() -> None:
    """Entry point for the ``snake-db`` console script."""
    serve()
