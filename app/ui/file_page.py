"""AES-GCM file encryption and decryption page."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services import file_service, history_service, key_service
from app.ui.widgets import build_page_header, make_button_row, make_status_label, set_status
from app.utils.exceptions import CryptoDeskError, DatabaseError, ValidationError
from app.utils.validators import validate_aes_key_b64, validate_password

logger = logging.getLogger(__name__)


class FilePage(QWidget):
    """Encrypt and decrypt arbitrary files with AES-256-GCM."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        title, description = build_page_header(
            "Bảo vệ tệp",
            "Mã hóa hoặc giải mã tệp tối đa 100 MB bằng AES-256-GCM.",
        )
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(("Mã hóa", "Giải mã"))
        self.auth_combo = QComboBox()
        self.auth_combo.addItems(("Khóa AES", "Mật khẩu"))

        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        input_button = QPushButton("Chọn tệp…")
        input_button.clicked.connect(self._browse_input)
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.addWidget(self.input_edit, 1)
        input_layout.addWidget(input_button)

        self.output_edit = QLineEdit()
        output_button = QPushButton("Chọn đầu ra…")
        output_button.clicked.connect(self._browse_output)
        output_widget = QWidget()
        output_layout = QHBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.addWidget(self.output_edit, 1)
        output_layout.addWidget(output_button)

        self.secret_edit = QLineEdit()
        self.secret_edit.setPlaceholderText("Khóa AES-256 dạng Base64")
        self.generate_button = QPushButton("Tạo khóa")
        self.generate_button.clicked.connect(self._generate_key)
        secret_widget = QWidget()
        secret_layout = QHBoxLayout(secret_widget)
        secret_layout.setContentsMargins(0, 0, 0, 0)
        secret_layout.addWidget(self.secret_edit, 1)
        secret_layout.addWidget(self.generate_button)

        self.run_button = QPushButton("Thực thi")
        self.run_button.setObjectName("primaryButton")
        self.run_button.clicked.connect(self._run)
        clear_button = QPushButton("Xóa")
        clear_button.clicked.connect(self._clear)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_label = make_status_label()

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Thao tác", self.mode_combo)
        form.addRow("Xác thực", self.auth_combo)
        form.addRow("Tệp đầu vào", input_widget)
        form.addRow("Tệp đầu ra", output_widget)
        form.addRow("Khóa/Mật khẩu", secret_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addWidget(self.progress)
        layout.addWidget(make_button_row(clear_button, self.run_button))
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.auth_combo.currentTextChanged.connect(self._update_auth_mode)
        self.mode_combo.currentTextChanged.connect(self._update_suggested_output)

    def _browse_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Chọn tệp đầu vào")
        if path:
            self.input_edit.setText(path)
            self._update_suggested_output()

    def _browse_output(self) -> None:
        suggested = self.output_edit.text() or "output.cdesk"
        path, _ = QFileDialog.getSaveFileName(self, "Chọn tệp đầu ra", suggested)
        if path:
            self.output_edit.setText(path)

    def _update_suggested_output(self, _value: str = "") -> None:
        if not self.input_edit.text():
            return
        source = Path(self.input_edit.text())
        if self.mode_combo.currentText() == "Mã hóa":
            suggested = source.with_name(source.name + ".cdesk")
        else:
            name = source.name.removesuffix(".cdesk")
            suggested = source.with_name(name + ".restored")
        self.output_edit.setText(str(suggested))

    def _update_auth_mode(self, mode: str) -> None:
        key_mode = mode == "Khóa AES"
        self.secret_edit.clear()
        self.secret_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if key_mode else QLineEdit.EchoMode.Password
        )
        self.secret_edit.setPlaceholderText(
            "Khóa AES-256 dạng Base64" if key_mode else "Nhập mật khẩu"
        )
        self.generate_button.setVisible(key_mode)

    def _generate_key(self) -> None:
        self.secret_edit.setText(key_service.generate_aes_key_b64())
        set_status(self.status_label, "Đã tạo khóa AES-256. Hãy lưu khóa an toàn.", True)
        self._record("GENERATE_KEY", True)

    def _run(self) -> None:
        input_path = Path(self.input_edit.text())
        output_path = Path(self.output_edit.text())
        encrypting = self.mode_combo.currentText() == "Mã hóa"
        operation = "ENCRYPT" if encrypting else "DECRYPT"
        completed = False
        try:
            if not self.input_edit.text():
                raise ValidationError("Vui lòng chọn tệp đầu vào.")
            if not self.output_edit.text():
                raise ValidationError("Vui lòng chọn tệp đầu ra.")
            if output_path.exists():
                answer = QMessageBox.question(
                    self,
                    "Xác nhận ghi đè",
                    "Tệp đầu ra đã tồn tại. Bạn có muốn ghi đè không?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    set_status(self.status_label, "Đã hủy thao tác.", False)
                    return

            self.run_button.setEnabled(False)
            self.progress.setRange(0, 0)
            set_status(self.status_label, "Đang xử lý tệp…", True)
            QApplication.processEvents()

            if self.auth_combo.currentText() == "Khóa AES":
                key = validate_aes_key_b64(self.secret_edit.text())
                if encrypting:
                    file_service.encrypt_file(input_path, output_path, key)
                else:
                    file_service.decrypt_file(input_path, output_path, key)
            else:
                password = validate_password(self.secret_edit.text())
                if encrypting:
                    file_service.encrypt_file_with_password(
                        input_path, output_path, password
                    )
                else:
                    file_service.decrypt_file_with_password(
                        input_path, output_path, password
                    )
            set_status(self.status_label, f"Hoàn tất: {output_path}", True)
            self._record(operation, True, input_path.name)
            completed = True
        except CryptoDeskError as exc:
            set_status(self.status_label, str(exc), False)
            self._record(operation, False, input_path.name or None)
        finally:
            self.progress.setRange(0, 100)
            self.progress.setValue(100 if completed else 0)
            self.run_button.setEnabled(True)

    def _record(
        self,
        operation: str,
        success: bool,
        source_name: str | None = None,
    ) -> None:
        algorithm = (
            "AES-256-GCM Key"
            if self.auth_combo.currentText() == "Khóa AES"
            else "AES-256-GCM Password"
        )
        try:
            history_service.add_history(
                operation,
                algorithm,
                "file",
                source_name,
                success,
                None if success else "invalid input",
            )
        except DatabaseError:
            logger.warning("Could not write file operation history")

    def _clear(self) -> None:
        self.input_edit.clear()
        self.output_edit.clear()
        self.secret_edit.clear()
        self.progress.setValue(0)
        self.status_label.clear()
