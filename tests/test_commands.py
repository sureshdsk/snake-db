"""Unit tests for the command registry and dispatch (PING/ECHO)."""

from __future__ import annotations

import pytest

from snake_db.commands import CommandRegistry, build_default_registry
from snake_db.db import SnakeDB
from snake_db.protocol import serialize


@pytest.fixture
def registry() -> CommandRegistry:
    return build_default_registry(SnakeDB())


def test_ping_no_args_returns_simple_pong(registry: CommandRegistry) -> None:
    assert _dispatch_reply(registry, b"PING") == ("simple", "PONG")


def test_ping_with_arg_returns_bulk_echo(registry: CommandRegistry) -> None:
    kind, value = _dispatch_reply(registry, b"PING", b"hi")
    assert kind == "bulk"
    assert value == b"hi"


def test_ping_too_many_args_returns_error(registry: CommandRegistry) -> None:
    kind, value = _dispatch_reply(registry, b"PING", b"a", b"b")
    assert kind == "error"
    assert "wrong number of arguments" in value


def test_echo_returns_bulk(registry: CommandRegistry) -> None:
    assert _dispatch_reply(registry, b"ECHO", b"hello") == ("bulk", b"hello")


def test_echo_wrong_arity(registry: CommandRegistry) -> None:
    kind, value = _dispatch_reply(registry, b"ECHO")
    assert kind == "error"
    assert "wrong number of arguments" in value


def test_command_names_are_case_insensitive(registry: CommandRegistry) -> None:
    assert _dispatch_reply(registry, b"ping") == ("simple", "PONG")
    assert _dispatch_reply(registry, b"PiNg") == ("simple", "PONG")


def test_unknown_command_returns_error(registry: CommandRegistry) -> None:
    kind, value = _dispatch_reply(registry, b"FROBNICATE", b"x")
    assert kind == "error"
    assert "unknown command" in value
    assert "FROBNICATE" in value


# --------------------------------------------------------------------------- #


def _dispatch_reply(registry: CommandRegistry, *args: bytes):
    """Dispatch and decode the reply into a ``(kind, value)`` tuple."""
    reply = registry.dispatch(list(args))
    return _decode_first(serialize(reply))


def _decode_first(data: bytes):
    """Tiny inline RESP decoder for the single reply in ``data``."""
    line, _, rest = data.partition(b"\r\n")
    kind_byte, rest_line = line[:1], line[1:]
    if kind_byte == b"+":
        return ("simple", rest_line.decode())
    if kind_byte == b"-":
        return ("error", rest_line.decode())
    if kind_byte == b":":
        return ("int", int(rest_line))
    if kind_byte == b"$":
        n = int(rest_line)
        if n == -1:
            return ("nil", None)
        return ("bulk", rest[:n])
    raise AssertionError(f"unexpected reply: {data!r}")
