from __future__ import annotations

from PyQt6.QtWidgets import QPushButton, QSizePolicy

from spaosi_voice_translator.ui.theme.colors import Colors


class RailButton(QPushButton):
    def __init__(self, text: str, *, accent: str = "grey", checkable: bool = False, parent=None):
        super().__init__(text, parent)
        self.accent = accent
        self.setCheckable(checkable)
        self.setFixedSize(78, 31)
        self.apply_style()

        if checkable:
            self.toggled.connect(self.apply_style)

    def apply_style(self, checked: bool | None = None) -> None:
        if checked is None:
            checked = self.isChecked() if self.isCheckable() else False

        accent_color = {
            "green": Colors.GREEN,
            "cyan": Colors.CYAN,
            "red": "#FF5555",
            "grey": "#AAAAAA",
        }.get(self.accent, "#AAAAAA")

        if self.isCheckable():
            bg = "#061406" if checked else "#101010"
            border = Colors.GREEN if checked else Colors.BORDER
            color = Colors.GREEN if checked else Colors.TEXT_DIM
        else:
            bg = "#151515"
            border = accent_color
            color = accent_color

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 5px;
                color: {color};
                font-size: 11px;
                font-weight: 900;
                padding: 3px 8px;
            }}
            QPushButton:hover {{
                background-color: #1D1D1D;
                border-color: {Colors.CYAN_DARK};
            }}
            QPushButton:pressed {{
                background-color: #080808;
            }}
            """
        )


class SettingsIconButton(RailButton):
    def __init__(self, parent=None):
        super().__init__("⚙", accent="cyan", parent=parent)
        self.setFixedSize(78, 31)

    def apply_style(self, checked: bool | None = None) -> None:
        super().apply_style(checked)
        self.setStyleSheet(
            self.styleSheet()
            + """
            QPushButton {
                font-size: 16px;
                font-family: "Segoe UI Symbol", "Segoe UI";
            }
            """
        )

    def set_active(self, active: bool) -> None:
        self.accent = "grey" if active else "cyan"
        self.apply_style()


class ToggleButton(QPushButton):
    def __init__(self, text: str, checked: bool = True, parent=None):
        super().__init__(parent)
        self.base_text = text
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggled.connect(self.apply_style)
        self.apply_style(self.isChecked())

    def set_base_text(self, text: str) -> None:
        self.base_text = text
        self.apply_style(self.isChecked())

    def apply_style(self, checked: bool) -> None:
        bg = "#061406" if checked else "#101010"
        border = Colors.GREEN if checked else Colors.BORDER
        color = Colors.GREEN if checked else Colors.TEXT_DIM
        suffix = "ON" if checked else "OFF"

        self.setText(f"{self.base_text} {suffix}")
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 5px;
                color: {color};
                font-size: 11px;
                font-weight: 900;
                padding: 4px 10px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #1D1D1D;
                border-color: {Colors.CYAN_DARK};
            }}
            """
        )