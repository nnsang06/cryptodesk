"""SQLite database initialization and connection management."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.utils.exceptions import DatabaseError

DEFAULT_DATABASE_PATH = Path("data/cryptodesk.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS operation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    input_type TEXT NOT NULL,
    source_name TEXT,
    success INTEGER NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL
)
"""


class Database:
    """Small connection factory for the local CryptoDesk database."""

    def __init__(self, path: Path = DEFAULT_DATABASE_PATH) -> None:
        self.path = Path(path)

    def initialize(self) -> None:
        """Create the containing directory and required tables."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.connect() as connection:
                connection.execute(SCHEMA)
        except sqlite3.Error as exc:
            raise DatabaseError("Không thể khởi tạo cơ sở dữ liệu lịch sử.") from exc
        except OSError as exc:
            raise DatabaseError("Không thể tạo thư mục dữ liệu.") from exc

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection configured to return named rows."""
        try:
            connection = sqlite3.connect(self.path)
            connection.row_factory = sqlite3.Row
            return connection
        except sqlite3.Error as exc:
            raise DatabaseError("Không thể kết nối cơ sở dữ liệu lịch sử.") from exc

