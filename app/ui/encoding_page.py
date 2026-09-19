"""Base64 and hexadecimal encoding page."""

from __future__ import annotations

import logging
from collections.abc import Callable

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.crypto import encoding_service
from app.services import history_service
from app.ui.widgets import build_page_header, copy_text, make_status_label, set_status
from app.utils.exceptions import CryptoDeskError, DatabaseError
from app.utils.validators import validate_non_empty_text

logger = logging.getLogger(__name__)


class EncodingPanel(QGroupBox):
    """Encode/decode form for one text representation."""

    def __init__(
        self,
        name: str,
        encoder: Callable[[str], str],
        decoder: Callable[[str], str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(name, parent)
        self.name = name
        self.encoder = encoder
        self.decoder = decoder

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Nhập văn bản hoặc dữ liệu đã encode")
        self.input_edit.setMaximumHeight(105)
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("Kết quả")
        self.output_edit.setMaximumHeight(105)
        self.status_label = make_status_label()

        encode_button = QPushButton("Encode")
        encode_button.setObjectName("primaryButton")
        encode_button.clicked.connect(lambda: self._run(True))
        decode_button = QPushButton("Decode")
        decode_button.clicked.connect(lambda: self._run(False))
        copy_button = QPushButton("Sao chép")
        copy_button.clicked.connect(
            lambda: copy_text(self.output_edit.toPlainText(), self.status_label)
        )
        clear_button = QPushButton("Xóa")
        clear_button.clicked.connect(self._clear)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(clear_button)
        buttons.addWidget(copy_button)
        buttons.addWidget(decode_button)
        buttons.addWidget(encode_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.input_edit)
        layout.addWidget(self.output_edit)
        layout.addLayout(buttons)
        layout.addWidget(self.status_label)

    def _run(self, encoding: bool) -> None:
        operation = "ENCODE" if encoding else "DECODE"
        try:
            value = validate_non_empty_text(self.input_edit.toPlainText(), "Đầu vào")
            result = self.encoder(value) if encoding else self.decoder(value)
            self.output_edit.setPlainText(result)
            set_status(self.status_label, f"{operation.title()} thành công.", True)
            self._record(operation, True)
        except CryptoDeskError as exc:
            self.output_edit.clear()
            set_status(self.status_label, str(exc), False)
            self._record(operation, False)

    def _record(self, operation: str, success: bool) -> None:
        try:
            history_service.add_history(
                operation,
                self.name,
                "text",
                None,
                success,
                None if success else "invalid input",
            )
        except DatabaseError:
            logger.warning("Could not write encoding operation history")

    def _clear(self) -> None:
        self.input_edit.clear()
        self.output_edit.clear()
        self.status_label.clear()


class EncodingPage(QWidget):
    """Provide UTF-8 Base64 and hexadecimal conversion tools."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        title, description = build_page_header(
            "Encoding",
            "Base64/Hex là encoding, không phải encryption và không bảo vệ bí mật dữ liệu.",
        )
        self.base64_panel = EncodingPanel(
            "Base64",
            encoding_service.base64_encode,
            encoding_service.base64_decode,
        )
        self.hex_panel = EncodingPanel(
            "Hex",
            encoding_service.hex_encode,
            encoding_service.hex_decode,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.base64_panel)
        layout.addWidget(self.hex_panel)
        layout.addStretch()
