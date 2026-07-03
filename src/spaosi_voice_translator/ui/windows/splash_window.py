import math

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from spaosi_voice_translator.core.app_icon import apply_icon_to_window
from spaosi_voice_translator.core.constants import APP_NAME


class CompactVoiceBarsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 74)
        self.frame = 0
        self.progress = 0.0
        self.bar_count = 20

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(42)

    def set_progress(self, value: float) -> None:
        self.progress = max(0.0, min(1.0, float(value)))
        self.update()

    def _tick(self) -> None:
        self.frame = (self.frame + 1) % 10_000
        self.update()

    def paintEvent(self, event) -> None:
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#000000"))

        bar_w = 5
        gap = 6
        total_w = self.bar_count * bar_w + (self.bar_count - 1) * gap
        start_x = (self.width() - total_w) // 2
        center_y = self.height() // 2 - 5

        loaded_until = int(self.progress * self.bar_count)
        scan_index = (self.frame // 2) % self.bar_count

        for i in range(self.bar_count):
            mid_distance = abs(i - (self.bar_count - 1) / 2) / ((self.bar_count - 1) / 2)
            center_power = 1.0 - mid_distance * 0.45

            wave = abs(math.sin(self.frame / 8.0 + i * 0.6))
            slow = abs(math.sin(self.frame / 20.0 + i * 0.2))
            power = (wave * 0.82 + slow * 0.18) * center_power

            bar_h = int(9 + power * 50)
            bar_h = max(8, min(bar_h, self.height() - 18))

            x = start_x + i * (bar_w + gap)
            y = center_y - bar_h // 2

            is_loaded = i <= loaded_until
            distance = abs(i - scan_index)

            if self.progress >= 1.0:
                if distance == 0:
                    color = QColor("#FFFFFF")
                elif distance == 1:
                    color = QColor("#00FFFF")
                else:
                    color = QColor("#00FF00")
            elif is_loaded:
                if distance == 0:
                    color = QColor("#00FFFF")
                elif distance == 1:
                    color = QColor("#00AA88")
                else:
                    color = QColor("#00FF00")
            else:
                color = QColor("#163016")

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(x, y, bar_w, bar_h, 2, 2)


class MinimalProgressLine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(128, 8)
        self.progress = 0.0
        self.ready = False

    def set_progress(self, value: float) -> None:
        self.progress = max(0.0, min(1.0, float(value)))
        self.ready = self.progress >= 1.0
        self.update()

    def paintEvent(self, event) -> None:
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#000000"))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor("#151515"))
        painter.drawRoundedRect(0, 2, self.width(), 4, 2, 2)

        fill_width = max(6, int(self.width() * self.progress))
        color = QColor("#00FF00" if self.ready else "#00AA88")
        painter.setBrush(color)
        painter.drawRoundedRect(0, 2, fill_width, 4, 2, 2)


class SplashWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        apply_icon_to_window(self)
        self.setFixedSize(340, 280)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setStyleSheet(
            """
            QWidget {
                background-color: #000000;
                border: none;
            }

            QLabel {
                background: transparent;
                border: none;
            }
            """
        )

        self.is_ready = False
        self.progress = 0.0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.bars = CompactVoiceBarsWidget()
        self.progress_line = MinimalProgressLine()

        self.corner_label = QLabel("spaosi-vt")
        self.corner_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.corner_label.setStyleSheet(
            """
            color: #242424;
            font-size: 10px;
            font-weight: 700;
            padding-right: 12px;
            padding-bottom: 10px;
            """
        )

        layout.addStretch(4)
        layout.addWidget(self.bars, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(12)
        layout.addWidget(self.progress_line, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(4)
        layout.addWidget(self.corner_label)

    def set_loading_text(self, text: str) -> None:
        del text

        if self.is_ready:
            return

        self.progress = min(0.92, self.progress + 0.23)
        self.bars.set_progress(self.progress)
        self.progress_line.set_progress(self.progress)

    def set_ready_to_continue(self) -> None:
        self.is_ready = True
        self.progress = 1.0
        self.bars.set_progress(1.0)
        self.progress_line.set_progress(1.0)