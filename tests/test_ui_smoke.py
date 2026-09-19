"""Headless smoke and integration tests for the PySide6 interface."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox

from app.crypto import rsa_service
from app.services import history_service
from app.services.history_service import HistoryService
from app.ui.decrypt_page import DecryptPage
from app.ui.encoding_page import EncodingPage
from app.ui.encrypt_page import EncryptPage
from app.ui.file_page import FilePage
from app.ui.hash_page import HashPage
from app.ui.history_page import HistoryPage
from app.ui.key_page import KeyPage
from app.ui.main_window import MainWindow


@pytest.fixture(scope="module")
def application() -> QApplication:
    """Return the single QApplication required by all UI tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def isolated_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep UI test history out of the application database."""
    monkeypatch.setattr(
        history_service,
        "_default_service",
        HistoryService(tmp_path / "ui-history.db"),
    )


def test_main_window_constructs_and_navigates_all_pages(
    application: QApplication,
) -> None:
    window = MainWindow()
    expected = [
        "Trang chủ",
        "Mã hóa",
        "Giải mã",
        "Tệp",
        "Khóa",
        "Hash",
        "Encoding",
        "Lịch sử",
        "Cài đặt",
    ]
    assert [window.sidebar.item(i).text() for i in range(9)] == expected
    assert window.page_stack.count() == 9

    for index in range(9):
        window.sidebar.setCurrentRow(index)
        application.processEvents()
        assert window.page_stack.currentIndex() == index
        assert window.page_stack.currentWidget().findChild(QLabel, "pageTitle")
    window.close()


def test_text_pages_execute_caesar_and_aes_round_trips(
    application: QApplication,
) -> None:
    encrypt_page = EncryptPage()
    decrypt_page = DecryptPage()

    encrypt_page.input_edit.setPlainText("Hello PTIT!")
    encrypt_page.parameter_edit.setText("5")
    encrypt_page._run()
    ciphertext = encrypt_page.result_edit.toPlainText()
    assert ciphertext == "Mjqqt UYNY!"

    decrypt_page.input_edit.setPlainText(ciphertext)
    decrypt_page.parameter_edit.setText("5")
    decrypt_page._run()
    assert decrypt_page.result_edit.toPlainText() == "Hello PTIT!"

    encrypt_page.algorithm_combo.setCurrentText("AES-256-GCM (Khóa)")
    encrypt_page._generate_aes_key()
    key = encrypt_page.parameter_edit.text()
    encrypt_page.input_edit.setPlainText("AES UI round trip 🔐")
    encrypt_page._run()

    decrypt_page.algorithm_combo.setCurrentText("AES-256-GCM (Khóa)")
    decrypt_page.parameter_edit.setText(key)
    decrypt_page.input_edit.setPlainText(encrypt_page.result_edit.toPlainText())
    decrypt_page._run()
    assert decrypt_page.result_edit.toPlainText() == "AES UI round trip 🔐"


def test_history_clear_requires_confirmation(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    history_service.add_history("HASH", "SHA-256", "text", None, True)
    page = HistoryPage()
    assert page.table.rowCount() == 1

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )
    page._confirm_clear()
    assert len(history_service.list_history()) == 1

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    page._confirm_clear()
    assert history_service.list_history() == []


def test_remaining_pages_execute_end_to_end_workflows(
    application: QApplication,
    tmp_path: Path,
) -> None:
    private_pem, public_pem = rsa_service.generate_key_pair()
    encrypt_page = EncryptPage()
    encrypt_page.algorithm_combo.setCurrentText("RSA-OAEP")
    encrypt_page.rsa_key_pem = public_pem
    encrypt_page.input_edit.setPlainText("RSA through UI")
    encrypt_page._run()
    rsa_ciphertext = encrypt_page.result_edit.toPlainText()

    decrypt_page = DecryptPage()
    decrypt_page.algorithm_combo.setCurrentText("RSA-OAEP")
    decrypt_page.rsa_key_pem = private_pem
    decrypt_page.input_edit.setPlainText(rsa_ciphertext)
    decrypt_page._run()
    assert decrypt_page.result_edit.toPlainText() == "RSA through UI"

    key_page = KeyPage()
    key_page._generate_aes()
    key_page._generate_rsa()
    assert key_page.aes_key_edit.text()
    assert key_page.private_pem and key_page.public_pem

    source = tmp_path / "ui-file.bin"
    encrypted = tmp_path / "ui-file.bin.cdesk"
    restored = tmp_path / "ui-file-restored.bin"
    source.write_bytes(bytes(range(128)))
    file_page = FilePage()
    file_page.input_edit.setText(str(source))
    file_page.output_edit.setText(str(encrypted))
    file_page.secret_edit.setText(key_page.aes_key_edit.text())
    file_page._run()
    assert encrypted.exists()
    file_page.mode_combo.setCurrentText("Giải mã")
    file_page.input_edit.setText(str(encrypted))
    file_page.output_edit.setText(str(restored))
    file_page._run()
    assert restored.read_bytes() == source.read_bytes()

    hash_page = HashPage()
    hash_page.text_input.setPlainText("integrity")
    hash_page._calculate()
    hash_page.expected_edit.setText(hash_page.result_edit.text().upper())
    hash_page._verify()
    assert hash_page.verify_result.text() == "MATCH"

    encoding_page = EncodingPage()
    encoding_page.base64_panel.input_edit.setPlainText("Xin chào")
    encoding_page.base64_panel._run(True)
    encoded = encoding_page.base64_panel.output_edit.toPlainText()
    encoding_page.base64_panel.input_edit.setPlainText(encoded)
    encoding_page.base64_panel._run(False)
    assert encoding_page.base64_panel.output_edit.toPlainText() == "Xin chào"
