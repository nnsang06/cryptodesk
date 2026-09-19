"""Text encryption page."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from app.ui.text_crypto_page import TextCryptoPage


class EncryptPage(TextCryptoPage):
    """Encrypt text using classical and modern algorithms."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(encrypting=True, parent=parent)
