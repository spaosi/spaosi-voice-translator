from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from spaosi_voice_translator.ui.theme.colors import Colors


class SettingsRow(QWidget):
    def __init__(self, label: str, widget: QWidget, parent=None):
        super().__init__(parent)
        self.setFixedHeight(42)
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.label_widget = QLabel(label)
        self.label_widget.setFixedWidth(172)
        self.label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.label_widget.setStyleSheet(
            f"""
            color: {Colors.TEXT_MUTED};
            font-size: 12px;
            font-weight: 800;
            background: transparent;
            border: none;
            """
        )

        widget.setMinimumWidth(260)
        widget.setMaximumWidth(420)

        layout.addWidget(self.label_widget)
        layout.addWidget(widget, 1)
        layout.addStretch(1)

    def set_label(self, label: str) -> None:
        self.label_widget.setText(label)


class SettingsContentPage(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            padding-bottom: 4px;
            """
        )
        self.layout.addWidget(self.title_label)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)

    def add_row(self, label: str, widget: QWidget) -> SettingsRow:
        row = SettingsRow(label, widget)
        self.layout.addWidget(row)
        return row

    def finish(self) -> None:
        self.layout.addStretch(1)