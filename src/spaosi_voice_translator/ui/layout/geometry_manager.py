from __future__ import annotations

from PyQt6.QtWidgets import QWidget

from spaosi_voice_translator.core.settings import SettingsStore


class GeometryManager:
    def __init__(self, settings: SettingsStore):
        self.settings = settings

    def restore(self, window: QWidget, key: str, fallback: tuple[int, int, int, int]) -> None:
        value = self.settings.get(f"geometry.{key}")

        if isinstance(value, list) and len(value) == 4 and all(isinstance(i, int) for i in value):
            x, y, w, h = value
        else:
            x, y, w, h = fallback

        window.setGeometry(x, y, w, h)

    def save(self, window: QWidget, key: str) -> None:
        geometry = window.geometry()
        self.settings.set(
            f"geometry.{key}",
            [geometry.x(), geometry.y(), geometry.width(), geometry.height()],
        )
