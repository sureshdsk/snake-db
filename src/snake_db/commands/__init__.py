"""Command handlers package.

``build_default_registry`` constructs a ``CommandRegistry`` with all built-in
handlers bound to a given ``SnakeDB`` instance.
"""

from __future__ import annotations

from ..db import SnakeDB
from .connection import ConnectionCommands
from .registry import CommandRegistry

__all__ = ["CommandRegistry", "build_default_registry"]


def build_default_registry(db: SnakeDB) -> CommandRegistry:
    """Construct a ``CommandRegistry`` with every built-in command registered."""
    registry = CommandRegistry()
    connection = ConnectionCommands(db)

    registry.register("PING", connection.ping)
    registry.register("ECHO", connection.echo)

    return registry
