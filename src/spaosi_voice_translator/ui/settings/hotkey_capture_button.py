from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QPushButton

from spaosi_voice_translator.ui.theme.colors import Colors


class HotkeyCaptureButton(QPushButton):
    hotkey_changed = pyqtSignal(str)

    MODIFIER_KEYS = {
        Qt.Key.Key_Control,
        Qt.Key.Key_Shift,
        Qt.Key.Key_Alt,
        Qt.Key.Key_Meta,
    }

    SPECIAL_KEYS = {
        Qt.Key.Key_Space: "space",
        Qt.Key.Key_Return: "enter",
        Qt.Key.Key_Enter: "enter",
        Qt.Key.Key_Backspace: "backspace",
        Qt.Key.Key_Tab: "tab",
        Qt.Key.Key_Escape: "esc",
        Qt.Key.Key_Delete: "delete",
        Qt.Key.Key_Insert: "insert",
        Qt.Key.Key_Home: "home",
        Qt.Key.Key_End: "end",
        Qt.Key.Key_PageUp: "page up",
        Qt.Key.Key_PageDown: "page down",
        Qt.Key.Key_Up: "up",
        Qt.Key.Key_Down: "down",
        Qt.Key.Key_Left: "left",
        Qt.Key.Key_Right: "right",
    }

    def __init__(self, value: str = "F2", parent=None):
        super().__init__(parent)
        self._hotkey = self._normalize(value)
        self._capturing = False
        self._idle_tooltip = "Нажми кнопку, затем нажми клавишу или комбинацию"
        self._capture_text = "НАЖМИ КЛАВИШУ..."
        self._capture_tooltip = "Нажми нужную клавишу. Esc — отмена"
        self._saved_prefix = "СОХРАНЕНО: "
        self.setFixedHeight(34)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setToolTip(self._idle_tooltip)
        self.clicked.connect(self.start_capture)
        self._apply_idle_style()
        self._render_value()

    def apply_translations(
        self,
        *,
        idle_tooltip: str,
        capture_text: str,
        capture_tooltip: str,
        saved_prefix: str,
    ) -> None:
        self._idle_tooltip = idle_tooltip
        self._capture_text = capture_text
        self._capture_tooltip = capture_tooltip
        self._saved_prefix = saved_prefix

        if self._capturing:
            self.setText(self._capture_text)
            self.setToolTip(self._capture_tooltip)
            return

        self.setToolTip(self._idle_tooltip)
        self._render_value()

    def hotkey(self) -> str:
        return self._hotkey or "f2"

    def set_hotkey(self, value: str) -> None:
        self._hotkey = self._normalize(value) or "f2"
        self._capturing = False
        self._safe_release_keyboard()
        self._apply_idle_style()
        self._render_value()

    def start_capture(self) -> None:
        self._capturing = True
        self.setText(self._capture_text)
        self.setToolTip(self._capture_tooltip)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.grabKeyboard()
        self._apply_capture_style()

    def keyPressEvent(self, event) -> None:
        if not self._capturing:
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key.Key_Escape:
            self.cancel_capture()
            event.accept()
            return

        if event.key() in self.MODIFIER_KEYS:
            event.accept()
            return

        hotkey = self._event_to_hotkey(event)
        if not hotkey:
            event.accept()
            return

        self._hotkey = hotkey
        self._capturing = False
        self._safe_release_keyboard()
        self._apply_saved_style()
        self._render_value(prefix=self._saved_prefix)
        self.hotkey_changed.emit(hotkey)

        QTimer.singleShot(900, self._finish_saved_state)
        event.accept()

    def focusOutEvent(self, event) -> None:
        if self._capturing:
            self.cancel_capture()

        super().focusOutEvent(event)

    def cancel_capture(self) -> None:
        self._capturing = False
        self._safe_release_keyboard()
        self._apply_idle_style()
        self._render_value()
        self.setToolTip(self._idle_tooltip)

    def _finish_saved_state(self) -> None:
        if self._capturing:
            return

        self._apply_idle_style()
        self._render_value()
        self.setToolTip(self._idle_tooltip)

    def _event_to_hotkey(self, event) -> str:
        key_name = self._key_name(event)
        if not key_name:
            return ""

        modifiers = event.modifiers()
        parts: list[str] = []

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("alt")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("windows")

        if key_name not in parts:
            parts.append(key_name)

        return "+".join(parts)

    def _key_name(self, event) -> str:
        key = event.key()

        if key in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[key]

        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F35:
            return f"f{key - Qt.Key.Key_F1 + 1}".lower()

        text = event.text()
        if text and text.strip() and len(text.strip()) == 1:
            return text.strip().lower()

        sequence_name = QKeySequence(key).toString(QKeySequence.SequenceFormat.PortableText)
        sequence_name = sequence_name.strip().lower()

        replacements = {
            "pgup": "page up",
            "pgdown": "page down",
            "del": "delete",
            "ins": "insert",
            "esc": "esc",
        }
        return replacements.get(sequence_name, sequence_name)

    def _normalize(self, value: str) -> str:
        clean = str(value or "").strip().lower()
        clean = clean.replace("control", "ctrl")
        clean = clean.replace("win+", "windows+")
        clean = clean.replace("cmd+", "windows+")
        clean = "+".join(part.strip() for part in clean.split("+") if part.strip())
        return clean

    def _display(self, value: str) -> str:
        parts = [part for part in self._normalize(value).split("+") if part]
        pretty = {
            "ctrl": "CTRL",
            "alt": "ALT",
            "shift": "SHIFT",
            "windows": "WIN",
            "space": "SPACE",
            "enter": "ENTER",
            "esc": "ESC",
            "delete": "DELETE",
            "backspace": "BACKSPACE",
            "tab": "TAB",
            "page up": "PAGE UP",
            "page down": "PAGE DOWN",
        }
        return " + ".join(pretty.get(part, part.upper()) for part in parts) or "F2"

    def _render_value(self, prefix: str = "") -> None:
        self.setText(f"{prefix}{self._display(self._hotkey)}")

    def _safe_release_keyboard(self) -> None:
        try:
            self.releaseKeyboard()
        except Exception:
            pass

    def _apply_idle_style(self) -> None:
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #111111;
                border: 1px solid {Colors.BORDER};
                border-radius: 5px;
                padding: 5px 9px;
                color: {Colors.TEXT};
                font-size: 12px;
                font-weight: 900;
                text-align: center;
            }}
            QPushButton:hover {{
                border-color: {Colors.CYAN_DARK};
                background-color: #151515;
            }}
            """
        )

    def _apply_capture_style(self) -> None:
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #062020;
                border: 1px solid {Colors.CYAN};
                border-radius: 5px;
                padding: 5px 9px;
                color: {Colors.CYAN};
                font-size: 12px;
                font-weight: 900;
                text-align: center;
            }}
            """
        )

    def _apply_saved_style(self) -> None:
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #061406;
                border: 1px solid {Colors.GREEN};
                border-radius: 5px;
                padding: 5px 9px;
                color: {Colors.GREEN};
                font-size: 12px;
                font-weight: 900;
                text-align: center;
            }}
            """
        )

