from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QDialog, QFrame, QLabel, QPushButton, QVBoxLayout

from spaosi_voice_translator.core.app_icon import apply_icon_to_window
from spaosi_voice_translator.core.i18n import Translator, UiLanguage
from spaosi_voice_translator.ui.theme.colors import Colors


class LanguageOptionButton(QPushButton):
    selected = pyqtSignal(str)

    def __init__(self, language: UiLanguage, parent=None):
        super().__init__(parent)
        self.language = language
        self.setText(language.label)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setEnabled(language.enabled)
        self.clicked.connect(lambda: self.selected.emit(language.code))
        self._apply_style()

    def _apply_style(self) -> None:
        if self.language.enabled:
            color = Colors.TEXT
            border = Colors.BORDER
            hover_border = Colors.CYAN_DARK
            background = "#111111"
        else:
            color = Colors.TEXT_DIM
            border = Colors.BORDER_DARKER
            hover_border = Colors.BORDER_DARKER
            background = "#080808"

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: 7px;
                color: {color};
                font-size: 13px;
                font-weight: 900;
                padding: 8px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #151515;
                border-color: {hover_border};
                color: {Colors.TEXT};
            }}
            QPushButton:disabled {{
                background-color: #080808;
                border-color: {Colors.BORDER_DARKER};
                color: {Colors.TEXT_DIM};
            }}
            """
        )


class LanguageSelectionDialog(QDialog):
    def __init__(self, translator: Translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle("Spaosi Voice Translator")
        apply_icon_to_window(self)
        self.setModal(True)
        self.setFixedSize(460, 430)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowTitleHint
        )
        self.setStyleSheet("background-color: #050505; color: #FFFFFF;")
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(0)

        surface = QFrame()
        surface.setObjectName("LanguageSurface")
        surface.setStyleSheet(
            f"""
            QFrame#LanguageSurface {{
                background-color: {Colors.PANEL_3};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
            }}
            """
        )
        root.addWidget(surface, 1)

        layout = QVBoxLayout(surface)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(14)

        title = QLabel(self.translator.t("language_dialog.title"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"""
            color: {Colors.TEXT};
            font-size: 20px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

        subtitle = QLabel(self.translator.t("language_dialog.subtitle"))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"""
            color: {Colors.TEXT_MUTED};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            border: none;
            """
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        buttons_container = QFrame()
        buttons_container.setStyleSheet("background: transparent; border: none;")
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(8)

        for language in self.translator.language_options():
            button = LanguageOptionButton(language)
            button.selected.connect(self._select_language)
            buttons_layout.addWidget(button)

        layout.addWidget(buttons_container)

        footer_line = QFrame()
        footer_line.setFixedHeight(1)
        footer_line.setStyleSheet(f"background-color: {Colors.BORDER_DARK}; border: none;")

        footer = QLabel(self.translator.t("language_dialog.footer"))
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

        layout.addStretch(1)
        layout.addWidget(footer_line)
        layout.addWidget(footer)

    def _select_language(self, language_code: str) -> None:
        self.translator.set_language(language_code, mark_selected=True)
        self.accept()
