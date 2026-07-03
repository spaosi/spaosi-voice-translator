from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout

from spaosi_voice_translator.app.app_context import AppContext
from spaosi_voice_translator.ui.theme.colors import Colors
from spaosi_voice_translator.ui.widgets.auto_resizing_label import AutoResizingLabel
from spaosi_voice_translator.ui.windows.base_overlay import BaseOverlay


class VoiceOverlayWindow(BaseOverlay):
    def __init__(self, context: AppContext):
        self.context = context
        super().__init__(self.context.translator.t("overlays.voice.title"), 800, 300)
        self.recording = False
        self._build_ui()
        self.context.signals.language_changed.connect(self.apply_translations)

    def _build_ui(self) -> None:
        self.screen = QFrame()
        self._set_screen_recording(False)

        screen_layout = QVBoxLayout(self.screen)
        screen_layout.setContentsMargins(18, 18, 18, 18)
        screen_layout.setSpacing(10)

        self.transcription = AutoResizingLabel(
            self.context.translator.t("voice.waiting"),
            base_font_size=34,
            min_font_size=12,
            bold=True,
            color=Colors.CYAN,
        )
        self.transcription.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.recording_hint = QLabel(self.context.translator.t("voice.press_hotkey_again"))
        self.recording_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recording_hint.setWordWrap(True)
        self.recording_hint.setVisible(False)
        self.recording_hint.setStyleSheet(
            f"""
            QLabel {{
                color: {Colors.CYAN};
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: 900;
                letter-spacing: 0.4px;
            }}
            """
        )

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {Colors.BORDER_DARK}; margin: 0 40px;")
        line.setFixedHeight(1)

        self.target = AutoResizingLabel(
            "",
            base_font_size=28,
            min_font_size=10,
            color=Colors.TEXT,
        )
        self.target.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.source = AutoResizingLabel(
            "",
            base_font_size=13,
            min_font_size=8,
            color=Colors.TEXT_DIM,
        )
        self.source.setAlignment(Qt.AlignmentFlag.AlignCenter)

        screen_layout.addWidget(self.transcription, 5)
        screen_layout.addWidget(self.recording_hint, 1)
        screen_layout.addWidget(line)
        screen_layout.addWidget(self.target, 4)
        screen_layout.addWidget(self.source, 1)

        self.content_layout.addWidget(self.screen, 1)

    def apply_translations(self, _language_code: str | None = None) -> None:
        self.set_overlay_title(self.context.translator.t("overlays.voice.title"))

        if self.recording:
            self.transcription.setText(self.context.translator.t("voice.listening"))
            self.recording_hint.setText(self.context.translator.t("voice.press_hotkey_again"))
        elif not self.target.text() and not self.source.text():
            self.transcription.setText(self.context.translator.t("voice.waiting"))

    def set_recording_state(self, is_recording: bool) -> None:
        self.recording = is_recording
        self._set_screen_recording(is_recording)

        if is_recording:
            self.transcription.setText(self.context.translator.t("voice.listening"))
            self.recording_hint.setText(self.context.translator.t("voice.press_hotkey_again"))
            self.recording_hint.setVisible(True)
            self.target.setText("")
            self.source.setText("")
            return

        self.recording_hint.setVisible(False)
        self.transcription.setText(self.context.translator.t("voice.waiting"))
        self.target.setText("")
        self.source.setText("")

    def set_voice_text(self, transcription: str, translation: str = "", source: str = "") -> None:
        if not self.recording:
            self.recording_hint.setVisible(False)

        self.transcription.setText(transcription)
        self.target.setText(translation)
        self.source.setText(source)

    def _set_screen_recording(self, is_recording: bool) -> None:
        border = Colors.CYAN_DARK if is_recording else Colors.BORDER_DARK
        self.screen.setStyleSheet(
            f"""
            QFrame {{
                background-color: {Colors.PANEL_2};
                border: 1px solid {border};
                border-radius: 6px;
            }}
            """
        )