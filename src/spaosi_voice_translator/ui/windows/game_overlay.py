from PyQt6.QtWidgets import QFrame, QVBoxLayout

from spaosi_voice_translator.app.app_context import AppContext
from spaosi_voice_translator.ui.theme.colors import Colors
from spaosi_voice_translator.ui.widgets.auto_resizing_label import AutoResizingLabel
from spaosi_voice_translator.ui.windows.base_overlay import BaseOverlay


class MessageItem(QFrame):
    def __init__(self, original: str, translated: str):
        super().__init__()
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.PANEL_3};
                border: 1px solid {Colors.BORDER};
                border-radius: 6px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)

        self.lbl_translated = AutoResizingLabel(
            translated,
            base_font_size=22,
            min_font_size=10,
            bold=True,
            color=Colors.ORANGE,
        )
        self.lbl_original = AutoResizingLabel(
            original,
            base_font_size=14,
            min_font_size=8,
            color=Colors.TEXT_MUTED,
        )

        layout.addWidget(self.lbl_translated, 10)
        layout.addWidget(self.lbl_original, 5)

    def set_dimmed(self) -> None:
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: #080808;
                border: 1px solid {Colors.BORDER_DARKER};
                border-radius: 6px;
            }}
            """
        )
        self.lbl_translated.set_color(Colors.ORANGE_DIM)
        self.lbl_original.set_color("#444444")


class GameOverlayWindow(BaseOverlay):
    def __init__(self, context: AppContext):
        self.context = context
        super().__init__(self.context.translator.t("overlays.game.title"), 600, 400)
        self.history: list[MessageItem] = []
        self.max_items = 3
        self.context.signals.language_changed.connect(self.apply_translations)

    def apply_translations(self, _language_code: str | None = None) -> None:
        self.set_overlay_title(self.context.translator.t("overlays.game.title"))

    def add_message(self, original: str, translated: str) -> None:
        for item in self.history:
            item.set_dimmed()

        widget = MessageItem(original, translated)
        self.content_layout.insertWidget(0, widget, stretch=1)
        self.history.insert(0, widget)

        while len(self.history) > self.max_items:
            old = self.history.pop()
            self.content_layout.removeWidget(old)
            old.deleteLater()
