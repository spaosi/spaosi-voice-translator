from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QSizeGrip, QVBoxLayout, QWidget

from spaosi_voice_translator.core.app_icon import apply_icon_to_window
from spaosi_voice_translator.ui.theme.colors import Colors
from spaosi_voice_translator.ui.widgets.title_bar import TitleBar


class BaseOverlay(QWidget):
    def __init__(self, title: str, width: int, height: int):
        super().__init__()
        self.setWindowTitle(title)
        apply_icon_to_window(self)
        self.resize(width, height)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("MainFrame")
        self.bg_frame.setStyleSheet(
            f"""
            QFrame#MainFrame {{
                background-color: {Colors.PANEL};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
            }}
            """
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.bg_frame)

        self.root_layout = QVBoxLayout(self.bg_frame)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.title_bar = TitleBar(title, self)
        self.root_layout.addWidget(self.title_bar)

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent; border: none;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(12, 12, 12, 20)
        self.content_layout.setSpacing(8)
        self.root_layout.addWidget(self.content, 1)

        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setStyleSheet("background: transparent; width: 20px; height: 20px;")

    def set_overlay_title(self, title: str) -> None:
        self.setWindowTitle(title)
        self.title_bar.set_title(title)

    def resizeEvent(self, event) -> None:
        self.sizegrip.move(self.width() - 20, self.height() - 20)
        super().resizeEvent(event)