"""Main application window and primary navigation."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.decrypt_page import DecryptPage
from app.ui.encoding_page import EncodingPage
from app.ui.encrypt_page import EncryptPage
from app.ui.file_page import FilePage
from app.ui.hash_page import HashPage
from app.ui.history_page import HistoryPage
from app.ui.home_page import HomePage
from app.ui.key_page import KeyPage
from app.ui.settings_page import SettingsPage


PageFactory = Callable[[], QWidget]


class MainWindow(QMainWindow):
    """Top-level CryptoDesk window with sidebar navigation."""

    NAVIGATION_ITEMS: tuple[tuple[str, PageFactory], ...] = (
        ("Trang chủ", HomePage),
        ("Mã hóa", EncryptPage),
        ("Giải mã", DecryptPage),
        ("Tệp", FilePage),
        ("Khóa", KeyPage),
        ("Hash", HashPage),
        ("Encoding", EncodingPage),
        ("Lịch sử", HistoryPage),
        ("Cài đặt", SettingsPage),
    )

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CryptoDesk")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(190)
        self.sidebar.setSpacing(2)

        self.page_stack = QStackedWidget()
        self.page_stack.setObjectName("pageStack")

        self._build_pages()
        self._build_layout()
        self._apply_styles()

        self.sidebar.currentRowChanged.connect(self.page_stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
        self.statusBar().showMessage("Sẵn sàng")

    def _build_pages(self) -> None:
        """Populate the sidebar and page stack in matching order."""
        for label, page_factory in self.NAVIGATION_ITEMS:
            item = QListWidgetItem(label)
            item.setSizeHint(QSize(0, 44))
            self.sidebar.addItem(item)
            self.page_stack.addWidget(page_factory())

    def _build_layout(self) -> None:
        """Build the header and main two-column layout."""
        brand = QLabel("CryptoDesk")
        brand.setObjectName("brand")

        header = QWidget()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 12, 22, 12)
        header_layout.addWidget(brand)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.page_stack, 1)

        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(header)
        central_layout.addWidget(content, 1)

        self.setCentralWidget(central_widget)

    def _apply_styles(self) -> None:
        """Apply a small baseline theme without external assets."""
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background-color: #f7f8fa;
                color: #172033;
                font-size: 14px;
            }
            QWidget#header {
                background-color: #172033;
            }
            QLabel#brand {
                background-color: transparent;
                color: white;
                font-size: 22px;
                font-weight: 700;
            }
            QListWidget#sidebar {
                background-color: #222d43;
                border: none;
                color: #dce4f2;
                outline: none;
                padding: 12px 8px;
            }
            QListWidget#sidebar::item {
                border-radius: 5px;
                padding-left: 12px;
            }
            QListWidget#sidebar::item:hover {
                background-color: #2f3d57;
            }
            QListWidget#sidebar::item:selected {
                background-color: #3d6ee8;
                color: white;
            }
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
            }
            QLabel#pageDescription {
                color: #536078;
                font-size: 15px;
            }
            QFrame#infoCard, QGroupBox {
                background-color: white;
                border: 1px solid #dce2eb;
                border-radius: 8px;
            }
            QGroupBox {
                font-weight: 700;
                margin-top: 10px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }
            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 700;
            }
            QLabel#cardBody {
                color: #536078;
            }
            QFrame#infoCard QLabel, QGroupBox QLabel {
                background-color: transparent;
            }
            QLabel#securityNotice {
                background-color: #fff7df;
                border: 1px solid #f0d787;
                border-radius: 7px;
                padding: 14px;
                color: #715300;
            }
            QLineEdit, QTextEdit, QComboBox, QTableWidget {
                background-color: white;
                border: 1px solid #cfd7e3;
                border-radius: 5px;
                padding: 7px;
                selection-background-color: #3d6ee8;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #3d6ee8;
            }
            QPushButton {
                background-color: #e9edf4;
                border: 1px solid #cfd7e3;
                border-radius: 5px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #dce4f1;
            }
            QPushButton#primaryButton {
                background-color: #3d6ee8;
                border-color: #3d6ee8;
                color: white;
                font-weight: 700;
            }
            QPushButton#primaryButton:hover {
                background-color: #315fcf;
            }
            QPushButton:disabled {
                color: #98a2b3;
                background-color: #eef1f5;
            }
            QLabel#statusLabel[state="success"] {
                color: #16794b;
            }
            QLabel#statusLabel[state="error"] {
                color: #c33636;
            }
            QLabel#verifyResult[matched="true"] {
                color: #16794b;
                font-weight: 700;
            }
            QLabel#verifyResult[matched="false"] {
                color: #c33636;
                font-weight: 700;
            }
            QProgressBar {
                border: 1px solid #cfd7e3;
                border-radius: 5px;
                background-color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3d6ee8;
                border-radius: 4px;
            }
            QStatusBar {
                background-color: white;
                border-top: 1px solid #e3e7ee;
            }
            """
        )
