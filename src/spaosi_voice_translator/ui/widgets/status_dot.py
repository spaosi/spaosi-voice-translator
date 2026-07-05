from PyQt6.QtWidgets import QFrame

from spaosi_voice_translator.ui.theme.colors import Colors


class StatusDot(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(13, 13)
        self.set_running(False)

    def set_running(self, running: bool) -> None:
        color = Colors.GREEN if running else "#551D1D"
        border = "#88FF88" if running else "#883333"
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {color};
                border: 1px solid {border};
                border-radius: 6px;
            }}
            """
        )
