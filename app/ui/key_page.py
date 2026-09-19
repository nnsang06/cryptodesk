"""AES and RSA key management page."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services import history_service, key_service
from app.ui.widgets import build_page_header, copy_text, make_status_label, set_status
from app.utils.exceptions import CryptoDeskError, DatabaseError

logger = logging.getLogger(__name__)


class KeyPage(QWidget):
    """Generate, import, inspect, and export AES/RSA keys."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.private_pem: bytes | None = None
        self.public_pem: bytes | None = None
        self.private_current_passphrase = ""

        title, description = build_page_header(
            "Quản lý khóa",
            "Tạo khóa AES-256/RSA và nhập hoặc xuất RSA key ở định dạng PEM.",
        )
        aes_group = self._build_aes_group()
        rsa_group = self._build_rsa_group()
        self.status_label = make_status_label()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(aes_group)
        layout.addWidget(rsa_group)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _build_aes_group(self) -> QGroupBox:
        group = QGroupBox("AES-256")
        self.aes_key_edit = QLineEdit()
        self.aes_key_edit.setReadOnly(True)
        self.aes_key_edit.setPlaceholderText("Khóa Base64 sẽ xuất hiện tại đây")
        generate_button = QPushButton("Tạo khóa AES")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate_aes)
        copy_button = QPushButton("Sao chép")
        copy_button.clicked.connect(
            lambda: copy_text(self.aes_key_edit.text(), self.status_label)
        )
        row = QHBoxLayout(group)
        row.addWidget(self.aes_key_edit, 1)
        row.addWidget(copy_button)
        row.addWidget(generate_button)
        return group

    def _build_rsa_group(self) -> QGroupBox:
        group = QGroupBox("RSA key pair")
        self.key_size_combo = QComboBox()
        self.key_size_combo.addItems(("2048", "3072"))
        self.metadata_label = QLabel("Chưa có RSA key trong bộ nhớ.")
        self.metadata_label.setWordWrap(True)
        self.passphrase_edit = QLineEdit()
        self.passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.passphrase_edit.setPlaceholderText("Dùng khi import private key được bảo vệ")
        self.export_passphrase_edit = QLineEdit()
        self.export_passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.export_passphrase_edit.setPlaceholderText(
            "Khuyến nghị nhập để bảo vệ private key khi export"
        )

        generate_button = QPushButton("Tạo RSA key pair")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate_rsa)
        import_public = QPushButton("Import public")
        import_public.clicked.connect(self._import_public)
        import_private = QPushButton("Import private")
        import_private.clicked.connect(self._import_private)
        export_public = QPushButton("Export public")
        export_public.clicked.connect(self._export_public)
        export_private = QPushButton("Export private")
        export_private.clicked.connect(self._export_private)

        buttons = QHBoxLayout()
        buttons.addWidget(import_public)
        buttons.addWidget(import_private)
        buttons.addStretch()
        buttons.addWidget(export_public)
        buttons.addWidget(export_private)
        buttons.addWidget(generate_button)

        form = QFormLayout(group)
        form.addRow("Kích thước", self.key_size_combo)
        form.addRow("Metadata", self.metadata_label)
        form.addRow("Passphrase hiện tại", self.passphrase_edit)
        form.addRow("Passphrase khi export", self.export_passphrase_edit)
        form.addRow(buttons)
        return group

    def _generate_aes(self) -> None:
        self.aes_key_edit.setText(key_service.generate_aes_key_b64())
        set_status(self.status_label, "Đã tạo khóa AES-256 mới.", True)
        self._record("GENERATE_KEY", "AES-256", True)

    def _generate_rsa(self) -> None:
        try:
            size = int(self.key_size_combo.currentText())
            self.private_pem, self.public_pem = key_service.generate_rsa_key_pair(size)
            self.private_current_passphrase = ""
            self.passphrase_edit.clear()
            self._update_metadata()
            set_status(self.status_label, "Đã tạo RSA key pair trong bộ nhớ.", True)
            self._record("GENERATE_KEY", f"RSA-{size}", True)
        except CryptoDeskError as exc:
            set_status(self.status_label, str(exc), False)
            self._record("GENERATE_KEY", "RSA", False)

    def _import_public(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import RSA public key", "", "PEM (*.pem *.key);;Tất cả tệp (*)"
        )
        if not path:
            return
        try:
            self.public_pem = key_service.import_public_key(Path(path))
            self._update_metadata()
            set_status(self.status_label, "Import public key thành công.", True)
            self._record("IMPORT_KEY", "RSA Public", True)
        except CryptoDeskError as exc:
            set_status(self.status_label, str(exc), False)
            self._record("IMPORT_KEY", "RSA Public", False)

    def _import_private(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Import RSA private key", "", "PEM (*.pem *.key);;Tất cả tệp (*)"
        )
        if not path:
            return
        try:
            passphrase = self.passphrase_edit.text()
            self.private_pem = key_service.import_private_key(Path(path), passphrase)
            self.private_current_passphrase = passphrase
            self._update_metadata()
            set_status(self.status_label, "Import private key thành công.", True)
            self._record("IMPORT_KEY", "RSA Private", True)
        except CryptoDeskError as exc:
            set_status(self.status_label, str(exc), False)
            self._record("IMPORT_KEY", "RSA Private", False)

    def _export_public(self) -> None:
        if self.public_pem is None:
            set_status(self.status_label, "Chưa có public key để export.", False)
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export RSA public key", "rsa_public.pem", "PEM (*.pem)"
        )
        if path:
            try:
                key_service.export_public_key(self.public_pem, Path(path))
                set_status(self.status_label, "Đã export public key.", True)
                self._record("EXPORT_KEY", "RSA Public", True)
            except CryptoDeskError as exc:
                set_status(self.status_label, str(exc), False)
                self._record("EXPORT_KEY", "RSA Public", False)

    def _export_private(self) -> None:
        if self.private_pem is None:
            set_status(self.status_label, "Chưa có private key để export.", False)
            return
        export_passphrase = self.export_passphrase_edit.text()
        if not export_passphrase:
            answer = QMessageBox.warning(
                self,
                "Private key không được bảo vệ",
                "Bạn đang export private key không có passphrase. Tiếp tục?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export RSA private key", "rsa_private.pem", "PEM (*.pem)"
        )
        if path:
            try:
                key_service.export_private_key(
                    self.private_pem,
                    Path(path),
                    export_passphrase,
                    self.private_current_passphrase,
                )
                set_status(self.status_label, "Đã export private key.", True)
                self._record("EXPORT_KEY", "RSA Private", True)
            except CryptoDeskError as exc:
                set_status(self.status_label, str(exc), False)
                self._record("EXPORT_KEY", "RSA Private", False)

    def _update_metadata(self) -> None:
        lines: list[str] = []
        if self.public_pem is not None:
            metadata = key_service.public_key_metadata(self.public_pem)
            lines.append(f"Public: {metadata['algorithm']} · {metadata['bits']} bit")
        if self.private_pem is not None:
            metadata = key_service.private_key_metadata(
                self.private_pem, self.private_current_passphrase
            )
            lines.append(f"Private: {metadata['algorithm']} · {metadata['bits']} bit")
        lines.append(f"Cập nhật: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')}")
        self.metadata_label.setText("\n".join(lines))

    @staticmethod
    def _record(operation: str, algorithm: str, success: bool) -> None:
        try:
            history_service.add_history(
                operation,
                algorithm,
                "key",
                None,
                success,
                None if success else "invalid key",
            )
        except DatabaseError:
            logger.warning("Could not write key operation history")
