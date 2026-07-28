"""Tests for the RESP2 serializer and the streaming CommandReader."""

from __future__ import annotations

from snake_db.protocol import (
    NIL,
    OK,
    Array,
    BulkString,
    CommandReader,
    Error,
    Integer,
)

# --------------------------------------------------------------------------- #
# serialize
# --------------------------------------------------------------------------- #


def test_serialize_simple_string() -> None:
    assert OK.serialize() == b"+OK\r\n"


def test_serialize_error() -> None:
    assert Error("WRONGTYPE foo").serialize() == b"-WRONGTYPE foo\r\n"


def test_serialize_integer() -> None:
    assert Integer(42).serialize() == b":42\r\n"
    assert Integer(-7).serialize() == b":-7\r\n"


def test_serialize_bulk_string() -> None:
    assert BulkString(b"hello").serialize() == b"$5\r\nhello\r\n"


def test_serialize_nil_bulk_string() -> None:
    assert NIL.serialize() == b"$-1\r\n"


def test_serialize_empty_bulk_string() -> None:
    assert BulkString(b"").serialize() == b"$0\r\n\r\n"


def test_serialize_array() -> None:
    assert Array([Integer(1), BulkString(b"x")]).serialize() == b"*2\r\n:1\r\n$1\r\nx\r\n"


# --------------------------------------------------------------------------- #
# CommandReader
# --------------------------------------------------------------------------- #


def test_reader_parses_array_command() -> None:
    reader = CommandReader()
    reader.feed(b"*1\r\n$4\r\nPING\r\n")
    assert reader.try_read_command() == [b"PING"]
    assert reader.try_read_command() is None


def test_reader_parses_inline_command() -> None:
    reader = CommandReader()
    reader.feed(b"PING\r\n")
    assert reader.try_read_command() == [b"PING"]


def test_reader_handles_partial_frames() -> None:
    reader = CommandReader()
    reader.feed(b"*2\r\n$3\r\nGET\r\n")
    assert reader.try_read_command() is None
    reader.feed(b"$1\r\nk\r\n")
    assert reader.try_read_command() == [b"GET", b"k"]


def test_reader_pipelines_multiple_commands() -> None:
    reader = CommandReader()
    reader.feed(b"*1\r\n$4\r\nPING\r\n*1\r\n$4\r\nPING\r\n")
    assert reader.try_read_command() == [b"PING"]
    assert reader.try_read_command() == [b"PING"]
    assert reader.try_read_command() is None


def test_reader_skips_blank_inline_lines() -> None:
    reader = CommandReader()
    reader.feed(b"\r\nPING\r\n")
    assert reader.try_read_command() == [b"PING"]
