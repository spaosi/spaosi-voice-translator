from __future__ import annotations

import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from spaosi_voice_translator.app.app_context import AppContext
from spaosi_voice_translator.app.window_manager import WindowManager
from spaosi_voice_translator.core.app_icon import apply_app_icon, configure_windows_taskbar_identity
from spaosi_voice_translator.core.constants import APP_NAME
from spaosi_voice_translator.ui.theme.stylesheet import build_app_stylesheet
from spaosi_voice_translator.ui.windows.language_selection_dialog import LanguageSelectionDialog
from spaosi_voice_translator.ui.windows.splash_window import SplashWindow


def run_app() -> int:
    configure_windows_taskbar_identity()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    apply_app_icon(app)
    app.setStyleSheet(build_app_stylesheet())

    context = AppContext()
    context.initialize()

    splash = SplashWindow()
    splash.show()

    manager = WindowManager(context)

    steps = [
        "audio input",
        "voice map",
        "overlays",
        "ready",
    ]

    state = {
        "index": 0,
        "windows_created": False,
    }

    def open_app() -> None:
        splash.close()

        if not context.translator.is_language_selected():
            dialog = LanguageSelectionDialog(context.translator)
            dialog.exec()
            context.settings.save()

        if not state["windows_created"]:
            manager.create_windows()
            state["windows_created"] = True

        manager.show_startup_layout()
        context.signals.app_ready.emit()

    def step() -> None:
        index = state["index"]

        if index < len(steps):
            splash.set_loading_text(steps[index])
            state["index"] += 1
            QTimer.singleShot(620, step)
            return

        splash.set_ready_to_continue()
        QTimer.singleShot(450, open_app)

    QTimer.singleShot(300, step)

    return app.exec()