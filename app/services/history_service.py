"""Safe metadata-only operation history service."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.database.database import DEFAULT_DATABASE_PATH, Database
from app.utils.exceptions import DatabaseError

_SAFE_MESSAGES = {
    "authentication failed",
    "invalid input",
    "invalid key",
    "file not found",
    "permission denied",
    "unsupported data",
    "operation cancelled",
}


class HistoryService:
    """Store only non-sensitive metadata about application operations."""

    def __init__(self, database_path: Path = DEFAULT_DATABASE_PATH) -> None:
        self.database = Database(database_path)
        self.database.initialize()

    def add_history(
        self,
        operation: str,
        algorithm: str,
        input_type: str,
        source_name: str | None,
        success: bool,
        message: str | None = None,
    ) -> None:
        """Append safe operation metadata; arbitrary messages are discarded."""
        safe_message = self._sanitize_message(message, success)
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        try:
            with self.database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO operation_history (
                        operation, algorithm, input_type, source_name,
                        success, message, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        operation.upper(),
                        algorithm,
                        input_type.lower(),
                        Path(source_name).name if source_name else None,
                        int(success),
                        safe_message,
                        created_at,
                    ),
                )
        except sqlite3.Error as exc:
            raise DatabaseError("Không thể ghi lịch sử thao tác.") from exc

    def list_history(self, limit: int = 100) -> list[dict[str, object]]:
        """Return newest history records first."""
        safe_limit = max(1, min(int(limit), 1000))
        try:
            with self.database.connect() as connection:
                rows = connection.execute(
                    """
                    SELECT id, operation, algorithm, input_type, source_name,
                           success, message, created_at
                    FROM operation_history
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (safe_limit,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise DatabaseError("Không thể đọc lịch sử thao tác.") from exc
        return [dict(row) for row in rows]

    def clear_history(self) -> None:
        """Delete all local operation history records."""
        try:
            with self.database.connect() as connection:
                connection.execute("DELETE FROM operation_history")
        except sqlite3.Error as exc:
            raise DatabaseError("Không thể xóa lịch sử thao tác.") from exc

    @staticmethod
    def _sanitize_message(message: str | None, success: bool) -> str:
        if message and message.strip().lower() in _SAFE_MESSAGES:
            return message.strip().lower()
        return "operation completed" if success else "operation failed"


_default_service: HistoryService | None = None


def _get_default_service() -> HistoryService:
    global _default_service
    if _default_service is None:
        _default_service = HistoryService()
    return _default_service


def add_history(
    operation: str,
    algorithm: str,
    input_type: str,
    source_name: str | None,
    success: bool,
    message: str | None = None,
) -> None:
    """Add a record to the default application history database."""
    _get_default_service().add_history(
        operation, algorithm, input_type, source_name, success, message
    )


def list_history(limit: int = 100) -> list[dict[str, object]]:
    """List records from the default application history database."""
    return _get_default_service().list_history(limit)


def clear_history() -> None:
    """Clear the default application history database."""
    _get_default_service().clear_history()

