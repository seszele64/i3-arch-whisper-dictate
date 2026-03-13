"""Database package for whisper-dictate.

This package provides async SQLite database operations using aiosqlite.
"""

from whisper_dictate.database import Database, get_database

__all__ = ["Database", "get_database"]
