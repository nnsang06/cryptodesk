"""Tests for metadata-only SQLite operation history."""

from pathlib import Path

from app.services.history_service import HistoryService


def test_add_list_and_clear_history(tmp_path: Path) -> None:
    service = HistoryService(tmp_path / "history.db")
    service.add_history("encrypt", "AES-256-GCM", "text", None, True)
    service.add_history("decrypt", "AES-256-GCM", "file", "/tmp/report.enc", False)

    records = service.list_history()
    assert len(records) == 2
    assert records[0]["operation"] == "DECRYPT"
    assert records[0]["source_name"] == "report.enc"
    assert records[0]["success"] == 0

    service.clear_history()
    assert service.list_history() == []


def test_history_discards_secrets_from_messages(tmp_path: Path) -> None:
    service = HistoryService(tmp_path / "history.db")
    secrets = [
        "password=correct horse battery staple",
        "AES_KEY=SW52YWxpZFNlY3JldEtleQ==",
        "-----BEGIN PRIVATE KEY----- private material",
        "plaintext: confidential report",
    ]
    for message in secrets:
        service.add_history("encrypt", "AES-256-GCM", "text", None, False, message)

    serialized = repr(service.list_history())
    for secret in secrets:
        assert secret not in serialized
    assert "operation failed" in serialized

