from __future__ import annotations

import ctypes
import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget

from spaosi_voice_translator.core.constants import APP_ORG


WINDOWS_APP_ID = f"{APP_ORG}.spaosi_voice_translator"


def configure_windows_taskbar_identity() -> None:
    """Make Windows taskbar group this app separately from python.exe."""

    if not sys.platform.startswith("win"):
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOWS_APP_ID)
    except Exception:
        pass


def find_app_icon_path() -> Path | None:
    """Find user-provided icon file.

    Preferred:
        actual/icon.png

    Also supported:
        actual/icon.ico
        actual/assets/icon.png
        actual/assets/icon.ico
        src/spaosi_voice_translator/assets/icon.png
        src/spaosi_voice_translator/assets/icon.ico
    """

    project_root = _project_root()

    candidates = (
        project_root / "icon.png",
        project_root / "icon.ico",
        project_root / "assets" / "icon.png",
        project_root / "assets" / "icon.ico",
        Path(__file__).resolve().parents[1] / "assets" / "icon.png",
        Path(__file__).resolve().parents[1] / "assets" / "icon.ico",
    )

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def load_app_icon() -> QIcon:
    path = find_app_icon_path()
    if not path:
        return QIcon()

    icon = QIcon(str(path))
    if icon.isNull():
        return QIcon()

    return icon


def apply_app_icon(app: QApplication) -> QIcon:
    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    return icon


def apply_icon_to_window(window: QWidget) -> None:
    app = QApplication.instance()
    if app is None:
        return

    icon = app.windowIcon()
    if not icon.isNull():
        window.setWindowIcon(icon)


def _project_root() -> Path:
    # src/spaosi_voice_translator/core/app_icon.py -> actual/
    return Path(__file__).resolve().parents[3]
