"""RESP2 (REdis Serialization Protocol) parser and serializer.

Reference: https://redis.io/docs/latest/develop/reference/protocol-spec/

Supported reply types:

  - Simple Strings: ``+OK\\r\\n``
  - Errors:         ``-ERR message\\r\\n``
  - Integers:       ``:1000\\r\\n``
  - Bulk Strings:   ``$6\\r\\nfoobar\\r\\n`` (binary-safe; ``$-1\\r\\n`` for nil)
  - Arrays:         ``*2\\r\\n...`` (``*-1\\r\\n`` for nil array)

Clients normally send commands as arrays of bulk strings, e.g.
``*1\\r\\n$4\\r\\nPING\\r\\n``. Inline commands (whitespace-separated text
terminated by a newline) are also accepted for interactive ``nc``/``telnet``
sessions.
"""

from __future__ import annotations

from dataclasses import dataclass

CRLF = b"\r\n"


# --------------------------------------------------------------------------- #
# Reply types
# --------------------------------------------------------------------------- #


@dataclass
class SimpleString:
    value: str

    def serialize(self) -> bytes:
        return b"+" + self.value.encode() + CRLF


@dataclass
class Error:
    message: str

    def serialize(self) -> bytes:
        return b"-" + self.message.encode() + CRLF


@dataclass
class Integer:
    value: int

    def serialize(self) -> bytes:
        return b":" + str(self.value).encode() + CRLF


@dataclass
class BulkString:
    value: bytes | None  # None -> nil bulk string ($-1)

    def serialize(self) -> bytes:
        if self.value is None:
            return b"$-1" + CRLF
        return b"$" + str(len(self.value)).encode() + CRLF + self.value + CRLF


@dataclass
class Array:
    items: list[Reply] | None  # None -> nil array (*-1)

    def serialize(self) -> bytes:
        if self.items is None:
            return b"*-1" + CRLF
        parts = [b"*" + str(len(self.items)).encode() + CRLF]
        parts += [item.serialize() for item in self.items]
        return b"".join(parts)


Reply = SimpleString | Error | Integer | BulkString | Array

OK = SimpleString("OK")
PONG = SimpleString("PONG")
NIL = BulkString(None)


# --------------------------------------------------------------------------- #
# Protocol errors
# --------------------------------------------------------------------------- #


class ProtocolError(Exception):
    """Raised when a client sends malformed RESP."""


# --------------------------------------------------------------------------- #
# Streaming command reader
# --------------------------------------------------------------------------- #


class CommandReader:
    """Incremental parser turning a byte stream into commands.

    ``feed`` appends received bytes; ``try_read_command`` returns the next
    fully-received command as a list of byte arguments, or ``None`` if more
    data is required. Pipelined commands come back one per call, and bytes
    for an incomplete command are retained until enough data arrives.
    """

    def __init__(self) -> None:
        self._buf = bytearray()

    def feed(self, data: bytes) -> None:
        self._buf.extend(data)

    def try_read_command(self) -> list[bytes] | None:
        """Parse and return the next non-empty command, or ``None`` if incomplete.

        Blank inline lines (and empty ``*0`` arrays) are skipped automatically.
        Raises ``ProtocolError`` on malformed input.
        """
        while True:
            if not self._buf:
                return None
            parsed = (
                self._parse_array() if self._buf[:1] == b"*" else self._parse_inline()
            )
            if parsed is None:
                return None
            if parsed:
                return parsed

    def _parse_array(self) -> list[bytes] | None:
        nl = self._buf.find(CRLF, 0)
        if nl == -1:
            return None
        try:
            count = int(self._buf[1:nl])
        except ValueError as exc:
            raise ProtocolError("invalid array length") from exc
        if count < 0:
            raise ProtocolError("negative array length")

        pos = nl + 2
        args: list[bytes] = []
        for _ in range(count):
            if pos >= len(self._buf):
                return None
            if self._buf[pos : pos + 1] != b"$":
                raise ProtocolError("expected bulk string element in array")
            head = self._buf.find(CRLF, pos)
            if head == -1:
                return None
            try:
                length = int(self._buf[pos + 1 : head])
            except ValueError as exc:
                raise ProtocolError("invalid bulk string length") from exc
            if length < 0:
                raise ProtocolError("negative bulk string length")
            data_start = head + 2
            data_end = data_start + length
            if data_end + 2 > len(self._buf):
                return None
            args.append(bytes(self._buf[data_start:data_end]))
            pos = data_end + 2

        del self._buf[:pos]
        return args

    def _parse_inline(self) -> list[bytes] | None:
        nl = self._buf.find(b"\n")
        if nl == -1:
            return None
        line = bytes(self._buf[:nl]).rstrip(b"\r")
        del self._buf[: nl + 1]
        if not line.strip():
            return []
        return line.split()
