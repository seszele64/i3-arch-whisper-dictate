"""Database package for whisper-dictate.

This package provides SQLite database operations using sqlite3.
"""

from whisper_dictate.database import Database, get_database

__all__ = ["Database", "get_database"]
