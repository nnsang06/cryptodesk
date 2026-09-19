"""CryptoDesk overview and safety guidance."""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from app.ui.widgets import InfoCard, build_page_header


class HomePage(QWidget):
    """Present the application modules and essential security guidance."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        title, description = build_page_header(
            "Trang chủ",
            "Bộ công cụ desktop hỗ trợ học tập và thao tác mật mã an toàn, cục bộ.",
        )

        cards = QGridLayout()
        cards.setSpacing(14)
        cards.addWidget(
            InfoCard("Mã hóa văn bản", "Caesar, Vigenère, AES-256-GCM và RSA-OAEP."),
            0,
            0,
        )
        cards.addWidget(
            InfoCard(
                "Bảo vệ tệp",
                "Mã hóa mọi loại tệp bằng AES-GCM với khóa hoặc mật khẩu.",
            ),
            0,
            1,
        )
        cards.addWidget(
            InfoCard(
                "Hash & Integrity",
                "Tính và kiểm tra SHA-256/SHA-512 cho text hoặc tệp.",
            ),
            1,
            0,
        )
        cards.addWidget(
            InfoCard(
                "Khóa & Encoding",
                "Quản lý khóa AES/RSA; chuyển đổi Base64 và Hex.",
            ),
            1,
            1,
        )

        warning = QLabel(
            "Lưu ý an toàn\n"
            "• Caesar và Vigenère chỉ dùng để học, không bảo vệ dữ liệu thực tế.\n"
            "• AES-GCM là lựa chọn chính để bảo vệ dữ liệu trong ứng dụng.\n"
            "• Base64/Hex là encoding, không phải encryption. Hash là một chiều."
        )
        warning.setObjectName("securityNotice")
        warning.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(cards)
        layout.addWidget(warning)
        layout.addStretch()
