"""Command registry and dispatch.

Handlers are registered by name and invoked through a ``CommandRegistry``
instance. Each handler takes the argument bytes following the command name and
returns a ``Reply`` (added in a later branch) or raises ``CommandError`` for
user-facing errors.
"""

from __future__ import annotations

from collections.abc import Callable

from ..protocol import Error, Reply

CommandFunc = Callable[[list[bytes]], Reply]


class CommandError(Exception):
    """Raised by handlers for user-facing errors (arity, type, overflow, ...)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CommandRegistry:
    """Case-insensitive lookup table of command name -> handler."""

    def __init__(self) -> None:
        self._handlers: dict[str, CommandFunc] = {}

    def register(self, name: str, fn: CommandFunc) -> CommandFunc:
        self._handlers[name.upper()] = fn
        return fn

    def dispatch(self, args: list[bytes]) -> Reply:
        """Look up and invoke the handler for ``args`` (command name first)."""
        if not args:
            return Error("ERR no command provided")
        raw_name = args[0].decode("utf-8", errors="replace")
        fn = self._handlers.get(raw_name.upper())
        if fn is None:
            return Error(f"ERR unknown command '{raw_name}'")
        try:
            return fn(args[1:])
        except CommandError as exc:
            return Error(exc.message)
