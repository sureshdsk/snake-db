"""Scaffold smoke: the package imports, exposes a version, and core classes exist."""

from __future__ import annotations

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
