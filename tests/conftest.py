"""Shared pytest fixtures."""

from __future__ import annotations

import socket
import threading

import pytest

from helpers import RespClient, wait_for_port
from snake_db.server import serve


@pytest.fixture
def free_port() -> int:
    """Return an ephemeral port that is free on loopback."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def server(free_port: int):
    """Start the server on a free port; yield ``(host, port)``.

    The server runs on a daemon thread (it has no graceful shutdown yet), so
    it is reaped when the test process exits. Each test gets a unique port.
    """
    host = "127.0.0.1"
    thread = threading.Thread(target=serve, args=(host, free_port), daemon=True)
    thread.start()
    wait_for_port(host, free_port)
    yield (host, free_port)


@pytest.fixture
def client(server):
    """A ``RespClient`` connected to the ``server`` fixture, closed after."""
    host, port = server
    cli = RespClient(host, port)
    yield cli
    cli.close()
