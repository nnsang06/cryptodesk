"""Shared text encryption/decryption page implementation."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.crypto import aes_service, caesar, rsa_service, vigenere
from app.services import history_service, key_service
from app.ui.widgets import (
    build_page_header,
    copy_text,
    make_button_row,
    make_status_label,
    set_status,
)
from app.utils.exceptions import CryptoDeskError, DatabaseError, ValidationError
from app.utils.validators import (
    validate_aes_key_b64,
    validate_non_empty_text,
    validate_password,
    validate_vigenere_key,
)

ALGORITHMS = (
    "Caesar",
    "Vigenère",
    "AES-256-GCM (Khóa)",
    "AES-256-GCM (Mật khẩu)",
    "RSA-OAEP",
)

logger = logging.getLogger(__name__)


class TextCryptoPage(QWidget):
    """Text crypto form used for encryption and decryption."""

    def __init__(self, encrypting: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.encrypting = encrypting
        self.rsa_key_pem: bytes | None = None

        title = "Mã hóa văn bản" if encrypting else "Giải mã văn bản"
        description = (
            "Chọn thuật toán, nhập dữ liệu và thông tin khóa phù hợp. "
            "Caesar/Vigenère chỉ dành cho mục đích học tập."
        )
        title_label, description_label = build_page_header(title, description)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.setObjectName("algorithmCombo")
        self.algorithm_combo.addItems(ALGORITHMS)

        self.input_edit = QTextEdit()
        self.input_edit.setObjectName("cryptoInput")
        self.input_edit.setPlaceholderText(
            "Nhập plaintext..." if encrypting else "Nhập ciphertext..."
        )
        self.input_edit.setMinimumHeight(115)

        self.parameter_label = QLabel("Shift")
        self.parameter_edit = QLineEdit()
        self.parameter_edit.setObjectName("cryptoParameter")
        self.parameter_edit.setText("3")

        self.generate_key_button = QPushButton("Tạo khóa AES")
        self.generate_key_button.clicked.connect(self._generate_aes_key)
        self.browse_key_button = QPushButton("Chọn PEM…")
        self.browse_key_button.clicked.connect(self._browse_rsa_key)

        parameter_widget = QWidget()
        parameter_layout = QHBoxLayout(parameter_widget)
        parameter_layout.setContentsMargins(0, 0, 0, 0)
        parameter_layout.addWidget(self.parameter_edit, 1)
        parameter_layout.addWidget(self.generate_key_button)
        parameter_layout.addWidget(self.browse_key_button)

        self.passphrase_label = QLabel("Passphrase private key")
        self.passphrase_edit = QLineEdit()
        self.passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.passphrase_edit.setPlaceholderText(
            "Để trống nếu private key không được bảo vệ"
        )

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Thuật toán", self.algorithm_combo)
        form.addRow("Dữ liệu đầu vào", self.input_edit)
        form.addRow(self.parameter_label, parameter_widget)
        form.addRow(self.passphrase_label, self.passphrase_edit)

        self.action_button = QPushButton("Mã hóa" if encrypting else "Giải mã")
        self.action_button.setObjectName("primaryButton")
        self.action_button.clicked.connect(self._run)
        self.copy_button = QPushButton("Sao chép")
        self.copy_button.clicked.connect(
            lambda: copy_text(self.result_edit.toPlainText(), self.status_label)
        )
        self.save_button = QPushButton("Lưu TXT…")
        self.save_button.clicked.connect(self._save_result)
        self.clear_button = QPushButton("Xóa")
        self.clear_button.clicked.connect(self._clear)

        self.result_edit = QTextEdit()
        self.result_edit.setObjectName("cryptoResult")
        self.result_edit.setReadOnly(True)
        self.result_edit.setPlaceholderText("Kết quả sẽ hiển thị tại đây")
        self.result_edit.setMinimumHeight(115)
        self.status_label = make_status_label()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addLayout(form)
        layout.addWidget(QLabel("Kết quả"))
        layout.addWidget(self.result_edit)
        layout.addWidget(
            make_button_row(
                self.clear_button,
                self.copy_button,
                self.save_button,
                self.action_button,
            )
        )
        layout.addWidget(self.status_label)

        self.algorithm_combo.currentTextChanged.connect(self._update_controls)
        self._update_controls(self.algorithm_combo.currentText())

    def _update_controls(self, algorithm: str) -> None:
        self.rsa_key_pem = None
        self.parameter_edit.clear()
        self.parameter_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        self.generate_key_button.setVisible(False)
        self.browse_key_button.setVisible(False)
        self.passphrase_label.setVisible(False)
        self.passphrase_edit.setVisible(False)

        if algorithm == "Caesar":
            self.parameter_label.setText("Shift")
            self.parameter_edit.setText("3")
            self.parameter_edit.setPlaceholderText("Ví dụ: 3")
        elif algorithm == "Vigenère":
            self.parameter_label.setText("Khóa Vigenère")
            self.parameter_edit.setPlaceholderText("Chỉ chữ cái A-Z/a-z")
        elif algorithm == "AES-256-GCM (Khóa)":
            self.parameter_label.setText("Khóa AES (Base64)")
            self.parameter_edit.setPlaceholderText("Khóa AES-256 dạng Base64")
            self.generate_key_button.setVisible(self.encrypting)
        elif algorithm == "AES-256-GCM (Mật khẩu)":
            self.parameter_label.setText("Mật khẩu")
            self.parameter_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.parameter_edit.setPlaceholderText("Nhập mật khẩu")
        else:
            key_type = "public" if self.encrypting else "private"
            self.parameter_label.setText(f"RSA {key_type} key")
            self.parameter_edit.setReadOnly(True)
            self.parameter_edit.setPlaceholderText(f"Chọn tệp {key_type} PEM")
            self.browse_key_button.setVisible(True)
            if not self.encrypting:
                self.passphrase_label.setVisible(True)
                self.passphrase_edit.setVisible(True)
        if algorithm != "RSA-OAEP":
            self.parameter_edit.setReadOnly(False)

    def _generate_aes_key(self) -> None:
        self.parameter_edit.setText(key_service.generate_aes_key_b64())
        set_status(
            self.status_label,
            "Đã tạo khóa AES-256 mới. Hãy lưu khóa an toàn.",
            True,
        )
        self._record("GENERATE_KEY", "AES-256", True)

    def _browse_rsa_key(self) -> None:
        path_value, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn RSA key",
            "",
            "PEM key (*.pem *.key);;Tất cả tệp (*)",
        )
        if not path_value:
            return
        try:
            path = Path(path_value)
            if self.encrypting:
                self.rsa_key_pem = key_service.import_public_key(path)
            else:
                self.rsa_key_pem = key_service.import_private_key(
                    path, self.passphrase_edit.text()
                )
            self.parameter_edit.setText(str(path))
            set_status(self.status_label, "Đã nạp và kiểm tra RSA key.", True)
        except CryptoDeskError as exc:
            self.rsa_key_pem = None
            set_status(self.status_label, str(exc), False)

    def _run(self) -> None:
        algorithm = self.algorithm_combo.currentText()
        try:
            input_text = validate_non_empty_text(
                self.input_edit.toPlainText(), "Dữ liệu đầu vào"
            )
            result = self._process(input_text, algorithm)
            self.result_edit.setPlainText(result)
            set_status(self.status_label, "Thao tác hoàn tất thành công.", True)
            self._record("ENCRYPT" if self.encrypting else "DECRYPT", algorithm, True)
        except (CryptoDeskError, ValueError) as exc:
            self.result_edit.clear()
            set_status(self.status_label, str(exc), False)
            self._record(
                "ENCRYPT" if self.encrypting else "DECRYPT",
                algorithm,
                False,
                "invalid input",
            )

    def _process(self, text: str, algorithm: str) -> str:
        parameter = self.parameter_edit.text()
        if algorithm == "Caesar":
            try:
                shift = int(parameter)
            except ValueError as exc:
                raise ValidationError("Shift phải là một số nguyên.") from exc
            return (
                caesar.encrypt(text, shift)
                if self.encrypting
                else caesar.decrypt(text, shift)
            )
        if algorithm == "Vigenère":
            key = validate_vigenere_key(parameter)
            return (
                vigenere.encrypt(text, key)
                if self.encrypting
                else vigenere.decrypt(text, key)
            )
        if algorithm == "AES-256-GCM (Khóa)":
            key = validate_aes_key_b64(parameter)
            return (
                aes_service.encrypt_text(text, key)
                if self.encrypting
                else aes_service.decrypt_text(text, key)
            )
        if algorithm == "AES-256-GCM (Mật khẩu)":
            password = validate_password(parameter)
            if self.encrypting:
                return aes_service.encrypt_text_with_password(text, password)
            return aes_service.decrypt_text_with_password(text, password)
        if self.rsa_key_pem is None:
            raise ValidationError("Vui lòng chọn và nạp RSA key PEM hợp lệ.")
        if self.encrypting:
            return rsa_service.encrypt_text(text, self.rsa_key_pem)
        password = self.passphrase_edit.text().encode("utf-8") or None
        return rsa_service.decrypt_text(text, self.rsa_key_pem, password)

    def _save_result(self) -> None:
        result = self.result_edit.toPlainText()
        if not result:
            set_status(self.status_label, "Chưa có kết quả để lưu.", False)
            return
        path_value, _ = QFileDialog.getSaveFileName(
            self, "Lưu kết quả", "result.txt", "Text (*.txt)"
        )
        if not path_value:
            return
        try:
            Path(path_value).write_text(result, encoding="utf-8")
            set_status(self.status_label, "Đã lưu kết quả.", True)
        except (PermissionError, OSError):
            set_status(self.status_label, "Không thể ghi tệp kết quả.", False)

    def _clear(self) -> None:
        self.input_edit.clear()
        self.result_edit.clear()
        self.status_label.clear()

    @staticmethod
    def _record(
        operation: str,
        algorithm: str,
        success: bool,
        message: str | None = None,
    ) -> None:
        try:
            history_service.add_history(
                operation, algorithm, "text", None, success, message
            )
        except DatabaseError:
            logger.warning("Could not write text operation history")
