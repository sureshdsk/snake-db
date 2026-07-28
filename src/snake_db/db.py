"""In-memory key-value database.

``SnakeDB`` is the shared, single-threaded store that will hold byte-string keys
and values with per-key TTL deadlines. Because the server runs on a single
thread, no locking is required.
"""

from __future__ import annotations


class SnakeDB:
    """Shared in-memory database (key/value and expiry are filled in later)."""

    def __init__(self) -> None:
        self._data: dict[bytes, bytes] = {}
        self._expiry: dict[bytes, int] = {}
