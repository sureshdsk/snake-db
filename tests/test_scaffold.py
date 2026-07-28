"""Scaffold smoke: the package imports, exposes a version, and echoes bytes."""

from __future__ import annotations

import socket

import snake_db
from snake_db.commands.registry import CommandRegistry
from snake_db.db import SnakeDB
from snake_db.server import RedisServer


def test_package_exposes_version() -> None:
    assert snake_db.__version__


def test_classes_exist() -> None:
    assert SnakeDB() is not None
    assert CommandRegistry() is not None
    assert RedisServer() is not None


def test_echo_server_round_trips_bytes(server) -> None:
    host, port = server
    with socket.create_connection((host, port), timeout=2.0) as s:
        s.sendall(b"hello\r\n")
        assert s.recv(64) == b"hello\r\n"
