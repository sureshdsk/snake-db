"""Shared argument-parsing helpers and constants for command handlers."""

from __future__ import annotations

from .registry import CommandError


def wrong_args(name: str) -> CommandError:
    return CommandError(f"ERR wrong number of arguments for '{name}' command")
