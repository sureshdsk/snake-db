"""TCP server.

A ``RedisServer`` owns a ``SnakeDB`` and a ``CommandRegistry``. This branch runs
a blocking, single-connection server that parses RESP2 from clients, dispatches
commands, and writes back serialized replies. The next branch upgrades it to
``asyncio`` for concurrent clients.
"""

from __future__ import annotations

import socket

from . import config, protocol
from .commands import build_default_registry
from .db import SnakeDB

_BUFFER_SIZE = 65536


class RedisServer:
    """A TCP server composing a database and a command registry."""

    def __init__(self) -> None:
        self.db = SnakeDB()
        self.registry = build_default_registry(self.db)

    def serve(self, host: str | None = None, port: str | int | None = None) -> None:
        """Run the blocking server until interrupted."""
        bind_host = host if host is not None else config.host()
        bind_port = int(port) if port is not None else config.port()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((bind_host, bind_port))
            listener.listen()
            print(f"snake-db listening on {(bind_host, bind_port)}", flush=True)
            while True:
                conn, _ = listener.accept()
                with conn:
                    self._handle(conn)

    def _handle(self, conn: socket.socket) -> None:
        reader = protocol.CommandReader()
        buf = bytearray()
        try:
            while True:
                data = conn.recv(_BUFFER_SIZE)
                if not data:
                    break
                buf.extend(data)
                reader.feed(data)
                try:
                    while True:
                        args = reader.try_read_command()
                        if args is None:
                            break
                        reply = self.registry.dispatch(args)
                        conn.sendall(reply.serialize())
                except protocol.ProtocolError as exc:
                    conn.sendall(
                        protocol.Error(f"ERR Protocol error: {exc}").serialize()
                    )
                    break
        except (ConnectionError, OSError):
            pass


def serve(host: str | None = None, port: str | int | None = None) -> None:
    """Run a default ``RedisServer`` (blocking) until interrupted."""
    RedisServer().serve(host, port)
