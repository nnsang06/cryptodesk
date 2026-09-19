"""Local metadata-only operation history page."""

from __future__ import annotations

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services import history_service
from app.ui.widgets import build_page_header, make_button_row, make_status_label, set_status
from app.utils.exceptions import DatabaseError


class HistoryPage(QWidget):
    """Display and clear the 100 newest operation metadata records."""

    HEADERS = (
        "ID",
        "Thao tác",
        "Thuật toán",
        "Loại",
        "Nguồn",
        "Trạng thái",
        "Thông báo",
        "Thời gian (UTC)",
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        title, description = build_page_header(
            "Lịch sử",
            "Chỉ lưu metadata thao tác; không lưu plaintext, password hoặc khóa bí mật.",
        )
        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        refresh_button = QPushButton("Làm mới")
        refresh_button.setObjectName("primaryButton")
        refresh_button.clicked.connect(self.refresh)
        clear_button = QPushButton("Xóa lịch sử")
        clear_button.clicked.connect(self._confirm_clear)
        self.status_label = make_status_label()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.table, 1)
        layout.addWidget(make_button_row(clear_button, refresh_button))
        layout.addWidget(self.status_label)

        self.refresh()

    def showEvent(self, event: QShowEvent) -> None:
        """Refresh records whenever the page becomes visible."""
        self.refresh()
        super().showEvent(event)

    def refresh(self) -> None:
        """Reload the newest records from SQLite."""
        try:
            records = history_service.list_history(100)
            self.table.setRowCount(len(records))
            for row_index, record in enumerate(records):
                values = (
                    record["id"],
                    record["operation"],
                    record["algorithm"],
                    record["input_type"],
                    record["source_name"] or "—",
                    "Thành công" if record["success"] else "Thất bại",
                    record["message"] or "—",
                    record["created_at"],
                )
                for column, value in enumerate(values):
                    self.table.setItem(row_index, column, QTableWidgetItem(str(value)))
            set_status(self.status_label, f"Đã tải {len(records)} bản ghi.", True)
        except DatabaseError as exc:
            set_status(self.status_label, str(exc), False)

    def _confirm_clear(self) -> None:
        answer = QMessageBox.question(
            self,
            "Xác nhận xóa lịch sử",
            "Bạn có chắc muốn xóa toàn bộ lịch sử thao tác?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            history_service.clear_history()
            self.refresh()
            set_status(self.status_label, "Đã xóa lịch sử.", True)
        except DatabaseError as exc:
            set_status(self.status_label, str(exc), False)
