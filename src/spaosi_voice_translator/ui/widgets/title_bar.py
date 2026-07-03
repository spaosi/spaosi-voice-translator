from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from spaosi_voice_translator.ui.theme.colors import Colors


class TitleBar(QWidget):
    def __init__(self, title: str, parent_window: QWidget):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self._drag_offset = None
        self.setFixedHeight(30)
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {Colors.PANEL_3};
                border-bottom: 1px solid {Colors.BORDER};
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)

        self.label = QLabel(title)
        self.label.setStyleSheet(
            f"""
            color: {Colors.TITLE};
            font-weight: 900;
            font-size: 11px;
            background: transparent;
            border: none;
            """
        )

        layout.addWidget(self.label)
        layout.addStretch()

    def set_title(self, title: str) -> None:
        self.label.setText(title)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_offset is not None:
            self.parent_window.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)