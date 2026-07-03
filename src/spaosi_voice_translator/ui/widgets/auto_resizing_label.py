from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QLabel, QSizePolicy


class AutoResizingLabel(QLabel):
    def __init__(
        self,
        text: str = "",
        *,
        base_font_size: int = 24,
        min_font_size: int = 8,
        bold: bool = False,
        color: str = "#FFFFFF",
        parent=None,
    ):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.base_font_size = base_font_size
        self.min_font_size = min_font_size
        self.bold = bold
        self.color = color
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.setMinimumSize(0, 0)
        self._apply_font(base_font_size)

    def set_color(self, color: str) -> None:
        self.color = color
        self._apply_font(self.font().pointSize())

    def setText(self, text: str) -> None:
        if text == self.text():
            return

        super().setText(text)
        self.adjust_font_to_fit()

    def resizeEvent(self, event) -> None:
        self.adjust_font_to_fit()
        super().resizeEvent(event)

    def adjust_font_to_fit(self) -> None:
        text = self.text()
        rect = self.contentsRect()

        if not text or rect.width() < 5 or rect.height() < 5:
            return

        for size in range(self.base_font_size, self.min_font_size - 1, -2):
            font = QFont("Segoe UI", size)
            font.setBold(self.bold)
            metrics = QFontMetrics(font)
            bounds = metrics.boundingRect(rect, Qt.TextFlag.TextWordWrap, text)

            if bounds.height() <= rect.height() and bounds.width() <= rect.width():
                self._apply_font(size)
                return

        self._apply_font(self.min_font_size)

    def _apply_font(self, size: int) -> None:
        font = QFont("Segoe UI", size)
        font.setBold(self.bold)
        self.setFont(font)
        self.setStyleSheet(f"color: {self.color}; background: transparent; border: none;")
