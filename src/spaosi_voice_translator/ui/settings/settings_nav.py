from __future__ import annotations

from PyQt6.QtWidgets import QPushButton

from spaosi_voice_translator.ui.theme.colors import Colors


class SettingsNavButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(34)
        self.setStyleSheet(self._style(False))

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self.setStyleSheet(self._style(checked))

    def _style(self, checked: bool) -> str:
        if checked:
            bg = "#062020"
            border = Colors.CYAN_DARK
            color = Colors.CYAN
        else:
            bg = "#0D0D0D"
            border = Colors.BORDER_DARK
            color = Colors.TEXT_MUTED

        return f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 5px;
                color: {color};
                font-size: 11px;
                font-weight: 900;
                padding: 6px 10px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #151515;
                border-color: {Colors.CYAN_DARK};
                color: {Colors.TEXT};
            }}
        """
