"""Reusable widgets and UI helpers shared by CryptoDesk pages."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def build_page_header(title: str, description: str) -> tuple[QLabel, QLabel]:
    """Create consistently styled title and description labels."""
    title_label = QLabel(title)
    title_label.setObjectName("pageTitle")
    description_label = QLabel(description)
    description_label.setObjectName("pageDescription")
    description_label.setWordWrap(True)
    return title_label, description_label


def make_status_label() -> QLabel:
    """Create a status label whose color is controlled by a state property."""
    label = QLabel("")
    label.setObjectName("statusLabel")
    label.setWordWrap(True)
    return label


def set_status(label: QLabel, message: str, success: bool) -> None:
    """Set status text and refresh its success/error styling."""
    label.setProperty("state", "success" if success else "error")
    label.setText(message)
    label.style().unpolish(label)
    label.style().polish(label)


def copy_text(text: str, status_label: QLabel | None = None) -> None:
    """Copy text to the system clipboard and optionally provide feedback."""
    if not text:
        if status_label is not None:
            set_status(status_label, "Chưa có nội dung để sao chép.", False)
        return
    QApplication.clipboard().setText(text)
    if status_label is not None:
        set_status(status_label, "Đã sao chép vào clipboard.", True)


class InfoCard(QFrame):
    """Compact title/body card used on the home and settings pages."""

    def __init__(self, title: str, body: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("infoCard")
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        body_label = QLabel(body)
        body_label.setWordWrap(True)
        body_label.setObjectName("cardBody")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.addWidget(title_label)
        layout.addWidget(body_label)
        layout.addStretch()


def make_button_row(*buttons: QPushButton) -> QWidget:
    """Place action buttons in a right-aligned row."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addStretch()
    for button in buttons:
        layout.addWidget(button)
    return container
