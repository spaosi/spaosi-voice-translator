from __future__ import annotations

import re
from datetime import datetime

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QFrame, QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from spaosi_voice_translator.app.app_context import AppContext
from spaosi_voice_translator.core.app_icon import apply_icon_to_window
from spaosi_voice_translator.core.log_localizer import localize_log_line
from spaosi_voice_translator.services.hotkeys.global_hotkey import GlobalHotkeyListener
from spaosi_voice_translator.services.pipeline.transcription_controller import (
    ExternalTranscriptionConfig,
    MicrophoneTranslationConfig,
    TranscriptionController,
)
from spaosi_voice_translator.ui.settings.settings_page import SettingsPage
from spaosi_voice_translator.ui.theme.colors import Colors
from spaosi_voice_translator.ui.widgets.audio_meter import AudioMeterCard
from spaosi_voice_translator.ui.widgets.buttons import RailButton, SettingsIconButton
from spaosi_voice_translator.ui.widgets.log_view import LogTextEdit
from spaosi_voice_translator.ui.widgets.status_dot import StatusDot


class MainWindow(QMainWindow):
    toggle_game_overlay = pyqtSignal(bool)
    toggle_voice_overlay = pyqtSignal(bool)
    external_translation = pyqtSignal(str, str)

    microphone_recording_state = pyqtSignal(bool)
    microphone_transcription = pyqtSignal(str)
    microphone_translation = pyqtSignal(str, str)

    request_quit = pyqtSignal()

    def __init__(self, context: AppContext):
        super().__init__()
        self.context = context
        self.translator = context.translator
        self.is_settings_page = False
        self.is_video_translation_mode = False

        self.transcription = TranscriptionController(self)
        self.transcription.log_line.connect(self.append_log)
        self.transcription.level_changed.connect(self.audio_card_safe_set_value)
        self.transcription.started.connect(self.on_transcription_started)
        self.transcription.stopped.connect(self.on_transcription_stopped)
        self.transcription.translation_ready.connect(self.external_translation.emit)

        self.transcription.microphone_recording_started.connect(self.on_microphone_recording_started)
        self.transcription.microphone_recording_stopped.connect(self.on_microphone_recording_stopped)
        self.transcription.microphone_transcription_changed.connect(self.on_microphone_transcription_changed)
        self.transcription.microphone_translation_ready.connect(self.on_microphone_translation_ready)

        self.hotkey_listener = GlobalHotkeyListener(self)
        self.hotkey_listener.pressed.connect(self.on_voice_hotkey_pressed)
        self.hotkey_listener.registered.connect(self.on_voice_hotkey_registered)
        self.hotkey_listener.error.connect(lambda line: self.append_log(line, "error"))

        self.setWindowTitle("spaosi-vt")
        apply_icon_to_window(self)
        self.resize(960, 500)
        self.setMinimumSize(860, 430)
        self.setStyleSheet(f"background-color: {Colors.APP_BG}; color: {Colors.TEXT};")

        self.context.signals.language_changed.connect(self.apply_translations)
        self._build_ui()
        self.apply_voice_hotkey_from_settings()

    def tr(self, key: str, **kwargs) -> str:
        return self.translator.t(key, **kwargs)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self._build_left_rail(root)
        self._build_main_area(root)

        self.set_video_translation_mode(self.settings_page.is_video_translation_mode())
        self.apply_translations()
        self.append_log(self.context.logger.info(self.tr("main.log.interface_loaded")), "system")
        self.append_log(self.tr("main.log.sys_idle"), "system")

    def _build_left_rail(self, root: QHBoxLayout) -> None:
        rail = QVBoxLayout()
        rail.setContentsMargins(0, 0, 0, 0)
        rail.setSpacing(8)
        root.addLayout(rail)

        self.audio_card = AudioMeterCard()
        self.audio_card.set_active(False)
        rail.addWidget(self.audio_card, 1)

        self.btn_start = RailButton("", accent="green")
        self.btn_start.clicked.connect(self.toggle_preview_state)
        rail.addWidget(self.btn_start)

        self.btn_settings = SettingsIconButton()
        self.btn_settings.clicked.connect(self.toggle_page)
        rail.addWidget(self.btn_settings)

    def _build_main_area(self, root: QHBoxLayout) -> None:
        main = QVBoxLayout()
        main.setSpacing(10)
        root.addLayout(main, 1)

        main.addWidget(self._build_top_line())

        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background: transparent; border: none;")
        main.addWidget(self.pages, 1)

        self.log = LogTextEdit()
        self.settings_page = SettingsPage(self, self.context.settings)

        self.pages.addWidget(self.log)
        self.pages.addWidget(self.settings_page)
        self.pages.setCurrentWidget(self.log)

    def _build_top_line(self) -> QFrame:
        top_line = QFrame()
        top_line.setFixedHeight(22)
        top_line.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(top_line)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.top_status_dot = StatusDot()

        self.mode_label = QLabel()
        self.mode_label.setFixedHeight(18)
        self.mode_label.setStyleSheet(
            f"""
            color: {Colors.CYAN};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

        self.mic_label = QLabel()
        self.mic_label.setFixedHeight(18)
        self.mic_label.setStyleSheet(
            f"""
            color: {Colors.TEXT_DIM};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {Colors.BORDER_DARK}; border: none;")

        layout.addWidget(self.top_status_dot)
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mic_label)
        layout.addWidget(divider, 1)

        return top_line

    def apply_translations(self, _language_code: str | None = None) -> None:
        if hasattr(self, "settings_page"):
            self.settings_page.apply_translations()

        if hasattr(self, "log"):
            self.log.apply_translations(
                incoming=self.tr("logs.filter.incoming"),
                translation=self.tr("logs.filter.translation"),
                system=self.tr("logs.filter.system"),
                errors=self.tr("logs.filter.errors"),
            )

        if hasattr(self, "audio_card"):
            self.audio_card.apply_translations(
                title=self.tr("audio.sys"),
                idle_text=self.tr("audio.idle"),
                active_text=self.tr("audio.active"),
                off_text=self.tr("audio.off"),
                idle_tooltip=self.tr("audio.tooltip_idle"),
                active_tooltip=self.tr("audio.tooltip_active"),
            )

        if hasattr(self, "btn_start"):
            self.btn_start.setText(
                self.tr("main.stop") if self.transcription.is_running else self.tr("main.start")
            )

        if hasattr(self, "mode_label"):
            self.set_video_translation_mode(self.is_video_translation_mode)

        if hasattr(self, "mic_label"):
            if self.transcription.is_mic_recording:
                self.mic_label.setText(self.tr("main.mic.recording"))
            else:
                hotkey = (
                    self.hotkey_listener.hotkey.upper()
                    if self.hotkey_listener.hotkey
                    else self.settings_page.voice_hotkey_value().upper()
                )
                self.mic_label.setText(self.tr("main.mic.idle", hotkey=hotkey))
                self.mic_label.setToolTip(self.tr("main.mic.tooltip", hotkey=hotkey))

    def set_video_translation_mode(self, enabled: bool) -> None:
        self.is_video_translation_mode = bool(enabled)

        if not hasattr(self, "mode_label"):
            return

        if self.is_video_translation_mode:
            self.mode_label.setText(self.tr("main.mode.video"))
            self.mode_label.setToolTip(self.tr("main.mode.video.tooltip"))
            self.mode_label.setStyleSheet(
                f"""
                color: {Colors.ORANGE};
                font-size: 10px;
                font-weight: 900;
                background: transparent;
                border: none;
                """
            )
            return

        self.mode_label.setText(self.tr("main.mode.realtime"))
        self.mode_label.setToolTip(self.tr("main.mode.realtime.tooltip"))
        self.mode_label.setStyleSheet(
            f"""
            color: {Colors.CYAN};
            font-size: 10px;
            font-weight: 900;
            background: transparent;
            border: none;
            """
        )

    def toggle_page(self) -> None:
        self.is_settings_page = not self.is_settings_page

        if self.is_settings_page:
            self.pages.setCurrentWidget(self.settings_page)
            self.btn_settings.set_active(True)
            return

        self.pages.setCurrentWidget(self.log)
        self.btn_settings.set_active(False)

    def toggle_preview_state(self) -> None:
        if self.transcription.is_running:
            self.transcription.stop()
            return

        self.start_external_transcription()

    def start_external_transcription(self) -> None:
        self.settings_page.save_to_store()
        self.context.settings.save()

        is_video_mode = self.settings_page.is_video_translation_mode()
        self.set_video_translation_mode(is_video_mode)

        config = ExternalTranscriptionConfig(
            api_key=self.settings_page.deepgram_key_value(),
            gemini_api_key=self.settings_page.gemini_key_value(),
            gemini_proxy_url=self.settings_page.gemini_proxy_url_value(),
            language=self.settings_page.language_code(),
            endpointing_ms=self.settings_page.system_endpointing_ms(),
            system_device_id=self.settings_page.selected_system_device_id(),
            video_translation_mode=is_video_mode,
            target_language_name=self.settings_page.target_language_name(),
        )
        self.transcription.start_external(config)

    def apply_voice_hotkey_from_settings(self) -> None:
        if not hasattr(self, "settings_page"):
            return

        self.settings_page.save_to_store()
        self.context.settings.save()

        hotkey = self.settings_page.voice_hotkey_value()
        self.hotkey_listener.register(hotkey)

    def on_voice_hotkey_pressed(self) -> None:
        self.settings_page.save_to_store()
        self.context.settings.save()

        config = MicrophoneTranslationConfig(
            api_key=self.settings_page.deepgram_key_value(),
            gemini_api_key=self.settings_page.gemini_key_value(),
            gemini_proxy_url=self.settings_page.gemini_proxy_url_value(),
            endpointing_ms=self.settings_page.microphone_endpointing_ms(),
            microphone_device_id=self.settings_page.selected_microphone_device_id(),
            recognition_language=self.settings_page.language_code(),
            recognition_language_name=self.settings_page.language_name(),
            target_language_name=self.settings_page.target_language_name(),
        )
        self.transcription.toggle_microphone_recording(config)

    def on_voice_hotkey_registered(self, hotkey: str) -> None:
        if hasattr(self, "mic_label"):
            self.mic_label.setText(self.tr("main.mic.idle", hotkey=hotkey))
            self.mic_label.setToolTip(self.tr("main.mic.tooltip", hotkey=hotkey))

        self.append_log(self.tr("main.log.hotkey_registered", hotkey=hotkey), "system")

    def on_microphone_recording_started(self) -> None:
        self.microphone_recording_state.emit(True)

        if hasattr(self, "mic_label"):
            self.mic_label.setText(self.tr("main.mic.recording"))
            self.mic_label.setStyleSheet(
                f"""
                color: {Colors.CYAN};
                font-size: 10px;
                font-weight: 900;
                background: transparent;
                border: none;
                """
            )

    def on_microphone_recording_stopped(self) -> None:
        self.microphone_recording_state.emit(False)

        if hasattr(self, "mic_label"):
            hotkey = self.hotkey_listener.hotkey.upper() if self.hotkey_listener.hotkey else self.settings_page.voice_hotkey_value().upper()
            self.mic_label.setText(self.tr("main.mic.idle", hotkey=hotkey))
            self.mic_label.setStyleSheet(
                f"""
                color: {Colors.TEXT_DIM};
                font-size: 10px;
                font-weight: 900;
                background: transparent;
                border: none;
                """
            )

    def on_microphone_transcription_changed(self, text: str) -> None:
        display_text = str(text or "")
        if display_text == "Слушаю...":
            display_text = self.tr("voice.listening")
        elif display_text == "Ожидание голоса":
            display_text = self.tr("voice.waiting")

        self.microphone_transcription.emit(display_text)

    def on_microphone_translation_ready(self, original: str, translated: str) -> None:
        self.microphone_translation.emit(original, translated)

    def on_transcription_started(self) -> None:
        self.audio_card.set_active(True)
        self.btn_start.setText(self.tr("main.stop"))
        self.btn_start.accent = "red"
        self.btn_start.apply_style()
        self.top_status_dot.set_running(True)

    def on_transcription_stopped(self) -> None:
        self.audio_card.set_active(False)
        self.btn_start.setText(self.tr("main.start"))
        self.btn_start.accent = "green"
        self.btn_start.apply_style()
        self.top_status_dot.set_running(False)

    def audio_card_safe_set_value(self, value: int) -> None:
        if hasattr(self, "audio_card"):
            self.audio_card.set_value(value)

    def append_log(self, line: str, category: str = "system") -> None:
        safe_line = localize_log_line(str(line), self.translator.language_code())

        if not re.match(r"^\d{2}:\d{2}:\d{2}:", safe_line):
            safe_line = f"{datetime.now().strftime('%H:%M:%S')}: {safe_line}"

        if hasattr(self.log, "append_log_line"):
            self.log.append_log_line(safe_line, category)
            return

        self.log.append(safe_line)

    def closeEvent(self, event) -> None:
        self.settings_page.save_to_store()

        self.hotkey_listener.unregister()

        if self.transcription.is_running:
            self.transcription.stop()

        self.transcription.stop_microphone_services()

        self.request_quit.emit()
        event.accept()
