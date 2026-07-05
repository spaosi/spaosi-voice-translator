from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QProgressBar, QSizePolicy, QVBoxLayout

from spaosi_voice_translator.ui.theme.colors import Colors


class AudioMeterCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_active = False
        self._title_text = "SYS"
        self._idle_text = "НЕ\nЗАПУЩЕНО"
        self._active_text = "СЛУШАЕТ"
        self._off_text = "OFF"
        self._idle_tooltip = "SYS: не запущено — звук системы не слушается"
        self._active_tooltip = "SYS: звук системы слушается"
        self.setMinimumSize(78, 180)
        self.setMaximumWidth(78)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.PANEL};
                border: 1px solid {Colors.BORDER};
                border-radius: 7px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 9, 8, 9)
        layout.setSpacing(8)

        self.title = QLabel(self._title_text)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 9px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

        self.meter = QProgressBar()
        self.meter.setOrientation(Qt.Orientation.Vertical)
        self.meter.setRange(0, 100)
        self.meter.setValue(0)
        self.meter.setTextVisible(False)
        self.meter.setFixedWidth(14)
        self.meter.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.status = QLabel(self._idle_text)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 8px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

        self.value = QLabel(self._off_text)
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

        layout.addWidget(self.title)
        layout.addWidget(self.meter, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.status)
        layout.addWidget(self.value)

        self.set_active(False)

    def apply_translations(
        self,
        *,
        title: str,
        idle_text: str,
        active_text: str,
        off_text: str,
        idle_tooltip: str,
        active_tooltip: str,
    ) -> None:
        self._title_text = title
        self._idle_text = idle_text
        self._active_text = active_text
        self._off_text = off_text
        self._idle_tooltip = idle_tooltip
        self._active_tooltip = active_tooltip

        self.title.setText(self._title_text)
        self.set_active(self.is_active)

    def set_active(self, active: bool) -> None:
        self.is_active = bool(active)

        if self.is_active:
            self.setToolTip(self._active_tooltip)
            self.status.setText(self._active_text)
            self.value.setText("0")
            self.meter.setValue(0)
            self._apply_active_style()
            return

        self.setToolTip(self._idle_tooltip)
        self.status.setText(self._idle_text)
        self.value.setText(self._off_text)
        self.meter.setValue(0)
        self._apply_idle_style()

    def set_value(self, value: int) -> None:
        if not self.is_active:
            self.meter.setValue(0)
            self.value.setText(self._off_text)
            return

        safe = max(0, min(100, int(value)))
        self.meter.setValue(safe)
        self.value.setText(str(safe))

    def _apply_idle_style(self) -> None:
        self.title.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 9px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )
        self.status.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 8px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )
        self.value.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

    def _apply_active_style(self) -> None:
        self.title.setStyleSheet(
            f"""
            color: {Colors.GREEN};
            font-size: 9px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )
        self.status.setStyleSheet(
            f"""
            color: {Colors.GREEN};
            font-size: 8px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )
        self.value.setStyleSheet(
            f"""
            color: {Colors.GREEN};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )