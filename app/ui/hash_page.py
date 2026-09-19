"""Hash calculation and verification page."""

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

from app.crypto import hash_service
from app.services import history_service
from app.ui.widgets import build_page_header, copy_text, make_status_label, set_status
from app.utils.exceptions import CryptoDeskError, DatabaseError, ValidationError

logger = logging.getLogger(__name__)


class HashPage(QWidget):
    """Calculate and verify SHA-256/SHA-512 digests for text and files."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        title, description = build_page_header(
            "Hash & Integrity",
            "Tính hoặc xác minh SHA-256/SHA-512. Hash là hàm một chiều, không thể giải mã.",
        )
        self.input_type_combo = QComboBox()
        self.input_type_combo.addItems(("Văn bản", "Tệp"))
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(("SHA-256", "SHA-512"))

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Nhập văn bản cần hash")
        self.text_input.setMaximumHeight(115)
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        file_button = QPushButton("Chọn tệp…")
        file_button.clicked.connect(self._browse_file)
        self.file_widget = QWidget()
        file_layout = QHBoxLayout(self.file_widget)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.addWidget(self.file_input, 1)
        file_layout.addWidget(file_button)

        self.result_edit = QLineEdit()
        self.result_edit.setReadOnly(True)
        self.expected_edit = QLineEdit()
        self.expected_edit.setPlaceholderText("Dán hash mong đợi để kiểm tra")
        self.verify_result = QLabel("")
        self.verify_result.setObjectName("verifyResult")
        self.status_label = make_status_label()

        calculate_button = QPushButton("Tính hash")
        calculate_button.setObjectName("primaryButton")
        calculate_button.clicked.connect(self._calculate)
        verify_button = QPushButton("Kiểm tra")
        verify_button.clicked.connect(self._verify)
        copy_button = QPushButton("Sao chép")
        copy_button.clicked.connect(
            lambda: copy_text(self.result_edit.text(), self.status_label)
        )
        clear_button = QPushButton("Xóa")
        clear_button.clicked.connect(self._clear)

        form = QFormLayout()
        form.addRow("Loại đầu vào", self.input_type_combo)
        form.addRow("Thuật toán", self.algorithm_combo)
        form.addRow("Văn bản", self.text_input)
        form.addRow("Tệp", self.file_widget)
        form.addRow("Hash", self.result_edit)
        form.addRow("Hash mong đợi", self.expected_edit)
        form.addRow("Kết quả kiểm tra", self.verify_result)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(clear_button)
        buttons.addWidget(copy_button)
        buttons.addWidget(verify_button)
        buttons.addWidget(calculate_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.input_type_combo.currentTextChanged.connect(self._update_input_type)
        self._update_input_type(self.input_type_combo.currentText())

    def _update_input_type(self, input_type: str) -> None:
        is_text = input_type == "Văn bản"
        self.text_input.setVisible(is_text)
        self.file_widget.setVisible(not is_text)

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Chọn tệp để hash")
        if path:
            self.file_input.setText(path)

    def _calculate(self) -> None:
        algorithm = self.algorithm_combo.currentText().lower().replace("-", "")
        input_type = self.input_type_combo.currentText()
        try:
            if input_type == "Văn bản":
                value = self.text_input.toPlainText()
                if not value:
                    raise ValidationError("Văn bản không được để trống.")
                digest = hash_service.hash_text(value, algorithm)
                source_name = None
            else:
                path = Path(self.file_input.text())
                digest = hash_service.hash_file(path, algorithm)
                source_name = path.name
            self.result_edit.setText(digest)
            self.verify_result.clear()
            set_status(self.status_label, "Đã tính hash thành công.", True)
            self._record("HASH", input_type, source_name, True)
        except CryptoDeskError as exc:
            self.result_edit.clear()
            set_status(self.status_label, str(exc), False)
            self._record("HASH", input_type, None, False)

    def _verify(self) -> None:
        actual = self.result_edit.text()
        expected = self.expected_edit.text()
        if not actual or not expected.strip():
            set_status(self.status_label, "Cần có hash thực tế và hash mong đợi.", False)
            return
        matched = hash_service.verify_hash(actual, expected)
        self.verify_result.setText("MATCH" if matched else "NOT MATCH")
        self.verify_result.setProperty("matched", matched)
        self.verify_result.style().unpolish(self.verify_result)
        self.verify_result.style().polish(self.verify_result)
        set_status(
            self.status_label,
            "Hash trùng khớp." if matched else "Hash không trùng khớp.",
            matched,
        )
        self._record("VERIFY_HASH", self.input_type_combo.currentText(), None, matched)

    def _record(
        self,
        operation: str,
        input_type: str,
        source_name: str | None,
        success: bool,
    ) -> None:
        try:
            history_service.add_history(
                operation,
                self.algorithm_combo.currentText(),
                "text" if input_type == "Văn bản" else "file",
                source_name,
                success,
            )
        except DatabaseError:
            logger.warning("Could not write hash operation history")

    def _clear(self) -> None:
        self.text_input.clear()
        self.file_input.clear()
        self.result_edit.clear()
        self.expected_edit.clear()
        self.verify_result.clear()
        self.status_label.clear()
