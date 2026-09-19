"""Useful runtime information and project details."""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QWidget

from app.crypto.aes_service import PBKDF2_ITERATIONS
from app.database.database import DEFAULT_DATABASE_PATH
from app.services.file_service import MAX_FILE_SIZE
from app.ui.widgets import InfoCard, build_page_header


class SettingsPage(QWidget):
    """Display meaningful fixed security and storage settings."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        title, description = build_page_header(
            "Cài đặt",
            "Thông tin cấu hình an toàn và lưu trữ đang được CryptoDesk sử dụng.",
        )
        grid = QGridLayout()
        grid.setSpacing(14)
        grid.addWidget(
            InfoCard("Dữ liệu cục bộ", f"Lịch sử: {DEFAULT_DATABASE_PATH}"), 0, 0
        )
        grid.addWidget(
            InfoCard(
                "Giới hạn tệp",
                f"Tối đa {MAX_FILE_SIZE // (1024 * 1024)} MB mỗi lần",
            ),
            0,
            1,
        )
        grid.addWidget(
            InfoCard(
                "Password KDF",
                f"PBKDF2-HMAC-SHA256 · {PBKDF2_ITERATIONS:,} vòng",
            ),
            1,
            0,
        )
        grid.addWidget(
            InfoCard("Giới thiệu", "CryptoDesk MVP · Python/PySide6"), 1, 1
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(grid)
        layout.addStretch()
