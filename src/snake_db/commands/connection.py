"""Connection commands: PING, ECHO."""

from __future__ import annotations

from ..db import SnakeDB
from ..protocol import BulkString, Reply, SimpleString
from ._helpers import wrong_args


class ConnectionCommands:
    """Handlers for connection-management commands."""

    def __init__(self, db: SnakeDB) -> None:
        self._db = db

    def ping(self, args: list[bytes]) -> Reply:
        if not args:
            return SimpleString("PONG")
        if len(args) == 1:
            return BulkString(args[0])
        raise wrong_args("ping")

    def echo(self, args: list[bytes]) -> Reply:
        if len(args) != 1:
            raise wrong_args("echo")
        return BulkString(args[0])
