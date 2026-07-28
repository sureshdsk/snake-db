"""Command registry and dispatch.

Handlers are registered by name and invoked through a ``CommandRegistry``
instance. Each handler takes the argument bytes following the command name and
returns a ``Reply`` (added in a later branch) or raises ``CommandError`` for
user-facing errors.
"""

from __future__ import annotations

from collections.abc import Callable


class CommandError(Exception):
    """Raised by handlers for user-facing errors (arity, type, overflow, ...)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CommandRegistry:
    """Case-insensitive lookup table of command name -> handler."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[list[bytes]], object]] = {}

    def register(self, name: str, fn: Callable[[list[bytes]], object]) -> None:
        self._handlers[name.upper()] = fn
