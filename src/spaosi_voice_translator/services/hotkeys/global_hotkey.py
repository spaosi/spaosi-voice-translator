from __future__ import annotations

import threading

from PyQt6.QtCore import QObject, pyqtSignal


class GlobalHotkeyListener(QObject):
    pressed = pyqtSignal()
    registered = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._keyboard = None
        self._handle = None
        self._hotkey = ""
        self._lock = threading.RLock()

    @property
    def hotkey(self) -> str:
        return self._hotkey

    def register(self, hotkey: str) -> bool:
        clean_hotkey = self._normalize_hotkey(hotkey)
        if not clean_hotkey:
            self.error.emit("Хоткей микрофона пустой")
            return False

        with self._lock:
            if clean_hotkey == self._hotkey and self._handle is not None:
                return True

            self.unregister()

            try:
                import keyboard
            except ImportError:
                self.error.emit(
                    "Ошибка хоткея: не хватает зависимости keyboard. "
                    "Установи зависимости через pip install -e ."
                )
                return False

            try:
                self._keyboard = keyboard
                self._handle = keyboard.add_hotkey(clean_hotkey, self._on_pressed, suppress=False)
                self._hotkey = clean_hotkey
                self.registered.emit(clean_hotkey.upper())
                return True
            except Exception as exc:
                self._keyboard = None
                self._handle = None
                self._hotkey = ""
                self.error.emit(f"Ошибка хоткея: не удалось зарегистрировать {clean_hotkey}: {exc}")
                return False

    def unregister(self) -> None:
        with self._lock:
            if self._keyboard is not None and self._handle is not None:
                try:
                    self._keyboard.remove_hotkey(self._handle)
                except Exception:
                    pass

            self._handle = None
            self._hotkey = ""

    def _on_pressed(self) -> None:
        self.pressed.emit()

    def _normalize_hotkey(self, hotkey: str) -> str:
        clean = str(hotkey or "").strip().lower()
        clean = clean.replace(" ", "")

        aliases = {
            "ctrl": "ctrl",
            "control": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "f1": "f1",
            "f2": "f2",
            "f3": "f3",
            "f4": "f4",
            "f5": "f5",
            "f6": "f6",
            "f7": "f7",
            "f8": "f8",
            "f9": "f9",
            "f10": "f10",
            "f11": "f11",
            "f12": "f12",
        }
        return aliases.get(clean, clean)
