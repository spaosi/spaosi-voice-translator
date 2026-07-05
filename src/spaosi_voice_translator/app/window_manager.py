from __future__ import annotations

from PyQt6.QtWidgets import QApplication

from spaosi_voice_translator.app.app_context import AppContext
from spaosi_voice_translator.services.obs.obs_server import obs_status, set_obs_text, start_obs_server
from spaosi_voice_translator.ui.layout.geometry_manager import GeometryManager
from spaosi_voice_translator.ui.windows.game_overlay import GameOverlayWindow
from spaosi_voice_translator.ui.windows.main_window import MainWindow
from spaosi_voice_translator.ui.windows.voice_overlay import VoiceOverlayWindow


class WindowManager:
    def __init__(self, context: AppContext):
        self.context = context
        self.geometry = GeometryManager(context.settings)
        self.main_window: MainWindow | None = None
        self.game_overlay: GameOverlayWindow | None = None
        self.voice_overlay: VoiceOverlayWindow | None = None
        self.obs_url = ""

    def create_windows(self) -> None:
        self.obs_url = start_obs_server(8088)
        self.context.settings.set("obs_widget_url", self.obs_url)

        self.main_window = MainWindow(self.context)
        self.game_overlay = GameOverlayWindow(self.context)
        self.voice_overlay = VoiceOverlayWindow(self.context)

        self.geometry.restore(self.main_window, "main_window", (1400, 420, 960, 500))
        self.geometry.restore(self.game_overlay, "game_overlay", (300, 260, 600, 400))
        self.geometry.restore(self.voice_overlay, "voice_overlay", (420, 700, 800, 350))

        self.main_window.toggle_game_overlay.connect(self.game_overlay.setVisible)
        self.main_window.toggle_voice_overlay.connect(self.voice_overlay.setVisible)

        self.main_window.external_translation.connect(self.game_overlay.add_message)
        self.main_window.external_translation.connect(self._send_external_translation_to_obs)

        self.main_window.microphone_recording_state.connect(self.voice_overlay.set_recording_state)
        self.main_window.microphone_transcription.connect(self._show_microphone_transcription)
        self.main_window.microphone_translation.connect(self._show_microphone_translation)
        self.main_window.microphone_translation.connect(self._send_microphone_translation_to_obs)

        self.main_window.request_quit.connect(self.close_all)
        self.context.signals.log_line.connect(self.main_window.append_log)

        self.context.signals.log_line.emit(self.context.logger.info(self.context.translator.t("app.windows_created")))

        started, error, url = obs_status()
        if started:
            self.context.signals.log_line.emit(self.context.logger.info(self.context.translator.t("app.obs_started", url=url)))
        elif error:
            self.context.signals.log_line.emit(self.context.logger.error(self.context.translator.t("app.obs_error", error=error)))

    def show_startup_layout(self) -> None:
        if not self.main_window or not self.game_overlay or not self.voice_overlay:
            return

        self.main_window.show()
        self.game_overlay.show()
        self.voice_overlay.show()
        self.context.signals.log_line.emit(self.context.logger.info(self.context.translator.t("app.ready")))

    def close_all(self) -> None:
        for key, window in (
            ("main_window", self.main_window),
            ("game_overlay", self.game_overlay),
            ("voice_overlay", self.voice_overlay),
        ):
            if window:
                self.geometry.save(window, key)

        self.context.settings.save()
        QApplication.quit()

    def _send_external_translation_to_obs(self, original: str, translated: str) -> None:
        del original

        video_mode = bool(
            self.main_window and getattr(self.main_window, "is_video_translation_mode", False)
        )
        result = set_obs_text(translated, is_mic=False, max_chars=0 if video_mode else None)

        if self.main_window and result.get("shown"):
            mode_suffix = "без обрезки" if video_mode else "обычный"
            self.main_window.append_log(
                f"OBS: показан текст ({mode_suffix}): {result.get('text', '')}",
                "system",
            )

    def _show_microphone_transcription(self, text: str) -> None:
        if not self.voice_overlay:
            return

        self.voice_overlay.set_voice_text(text, "", "")

    def _show_microphone_translation(self, original: str, translated: str) -> None:
        if not self.voice_overlay:
            return

        self.voice_overlay.set_voice_text(self.context.translator.t("voice.translation_ready"), translated, original)

    def _send_microphone_translation_to_obs(self, original: str, translated: str) -> None:
        del original

        result = set_obs_text(translated, is_mic=True, mic_prefix=True)

        if self.main_window and result.get("shown"):
            self.main_window.append_log(
                f"OBS: показан MIC текст: {result.get('text', '')}",
                "system",
            )