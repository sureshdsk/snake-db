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


def encode_command(args: list[bytes]) -> bytes:
    """Encode a command (list of byte args) as a RESP2 array of bulk strings."""
    parts = [b"*" + str(len(args)).encode() + b"\r\n"]
    for arg in args:
        parts.append(b"$" + str(len(arg)).encode() + b"\r\n" + arg + b"\r\n")
    return b"".join(parts)


Reply = tuple[str, object]


class RespClient:
    """Minimal blocking RESP2 client for integration tests.

    ``read_reply`` returns a ``(kind, value)`` tuple where kind is one of
    ``simple``, ``error``, ``int``, ``bulk``, ``nil``, ``array``,
    ``nil-array``.
    """

    def __init__(self, host: str, port: int, *, timeout: float = 2.0) -> None:
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._sock.settimeout(timeout)
        self._buf = bytearray()

    def send(self, *args: bytes | str) -> None:
        encoded = [a.encode() if isinstance(a, str) else a for a in args]
        self._sock.sendall(encode_command(encoded))

    def cmd(self, *args: bytes | str) -> Reply:
        """Send a command and read exactly one reply."""
        self.send(*args)
        return self.read_reply()

    def send_raw(self, data: bytes) -> None:
        self._sock.sendall(data)

    def read_reply(self) -> Reply:
        line = self._read_line()
        kind = line[:1]
        rest = line[1:]
        if kind == b"+":
            return ("simple", rest.decode())
        if kind == b"-":
            return ("error", rest.decode())
        if kind == b":":
            return ("int", int(rest))
        if kind == b"$":
            n = int(rest)
            if n == -1:
                return ("nil", None)
            return ("bulk", self._read_exact(n))
        if kind == b"*":
            n = int(rest)
            if n == -1:
                return ("nil-array", None)
            return ("array", [self.read_reply() for _ in range(n)])
        raise ValueError(f"unexpected reply kind {kind!r}")

    def close(self) -> None:
        self._sock.close()

    def _read_line(self) -> bytes:
        while b"\r\n" not in self._buf:
            self._extend()
        idx = self._buf.index(b"\r\n")
        line = bytes(self._buf[:idx])
        del self._buf[: idx + 2]
        return line

    def _read_exact(self, n: int) -> bytes:
        while len(self._buf) < n + 2:
            self._extend()
        data = bytes(self._buf[:n])
        del self._buf[: n + 2]
        return data

    def _extend(self) -> None:
        chunk = self._sock.recv(65536)
        if not chunk:
            raise ConnectionError("server closed the connection")
        self._buf.extend(chunk)
