"""Command handlers package.

``build_default_registry`` constructs a ``CommandRegistry`` with all built-in
handlers bound to a given ``SnakeDB`` instance. No commands are registered yet;
later branches add them here.
"""

from __future__ import annotations

from ..db import SnakeDB
from .registry import CommandRegistry

__all__ = ["CommandRegistry", "build_default_registry"]


def build_default_registry(db: SnakeDB) -> CommandRegistry:
    """Construct a ``CommandRegistry`` with every built-in command registered."""
    return CommandRegistry()
