"""Test utilities shared across the suite."""

from __future__ import annotations

import socket
import time


def wait_for_port(host: str, port: int, *, timeout: float = 2.0) -> None:
    """Block until a TCP server is accepting connections on ``host:port``.

    Raises ``TimeoutError`` if the server does not become ready within
    ``timeout`` seconds.
    """
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.25):
                return
        except OSError as exc:
            last_error = exc
            time.sleep(0.02)
    raise TimeoutError(
        f"server at {host}:{port} did not start within {timeout}s"
    ) from last_error
