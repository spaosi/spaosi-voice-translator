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
    """Find the app icon in source mode and in the PyInstaller bundle."""

    candidates: list[Path] = []

    bundle_root = getattr(sys, "_MEIPASS", "")
    if bundle_root:
        bundle = Path(str(bundle_root))
        candidates.extend(
            (
                bundle / "icon.ico",
                bundle / "icon.png",
                bundle / "assets" / "icon.ico",
                bundle / "assets" / "icon.png",
            )
        )

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.extend(
            (
                exe_dir / "icon.ico",
                exe_dir / "icon.png",
                exe_dir / "assets" / "icon.ico",
                exe_dir / "assets" / "icon.png",
            )
        )

    project_root = _project_root()
    candidates.extend(
        (
            project_root / "icon.ico",
            project_root / "icon.png",
            project_root / "assets" / "icon.ico",
            project_root / "assets" / "icon.png",
            Path(__file__).resolve().parents[1] / "assets" / "icon.ico",
            Path(__file__).resolve().parents[1] / "assets" / "icon.png",
        )
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
    return Path(__file__).resolve().parents[3]
