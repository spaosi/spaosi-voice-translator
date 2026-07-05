from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

from spaosi_voice_translator.services.audio.windows_audio import (
    WindowsMicrophoneCapture,
    WindowsSystemAudioCapture,
)
from spaosi_voice_translator.services.pipeline.phrase_segmenter import RealtimePhraseSegmenter
from spaosi_voice_translator.services.speech.deepgram_engine import DeepgramEngine
from spaosi_voice_translator.services.translation.gemini_translator import GeminiTranslator


@dataclass(frozen=True)
class ExternalTranscriptionConfig:
    api_key: str
    language: str
    endpointing_ms: int
    system_device_id: str = ""
    gemini_api_key: str = ""
    gemini_proxy_url: str = ""
    video_translation_mode: bool = False
    target_language_name: str = "Русский"


@dataclass(frozen=True)
class MicrophoneTranslationConfig:
    api_key: str
    gemini_api_key: str
    endpointing_ms: int
    gemini_proxy_url: str = ""
    microphone_device_id: str = ""
    recognition_language: str = "ru"
    recognition_language_name: str = "Russian"
    target_language_name: str = "Русский"


class TranscriptionController(QObject):
    log_line = pyqtSignal(str, str)
    level_changed = pyqtSignal(int)
    incoming_text = pyqtSignal(str)
    translation_ready = pyqtSignal(str, str)

    microphone_recording_started = pyqtSignal()
    microphone_recording_stopped = pyqtSignal()
    microphone_transcription_changed = pyqtSignal(str)
    microphone_translation_ready = pyqtSignal(str, str)

    started = pyqtSignal()
    stopped = pyqtSignal()
    ready = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.system_audio: WindowsSystemAudioCapture | None = None
        self.deepgram_external: DeepgramEngine | None = None
        self.gemini_external: GeminiTranslator | None = None
        self.external_segmenter = RealtimePhraseSegmenter()
        self.video_translation_mode = False

        self.is_mic_recording = False
        self.microphone_audio: WindowsMicrophoneCapture | None = None
        self.deepgram_mic: DeepgramEngine | None = None
        self.gemini_mic: GeminiTranslator | None = None
        self.microphone_runtime_signature: tuple[str, int, str, str] | None = None
        self.mic_accumulated_text = ""

    def start_external(self, config: ExternalTranscriptionConfig) -> bool:
        if self.is_running:
            return False

        if not config.api_key:
            self.log_line.emit("Ошибка: ключ Deepgram пустой", "error")
            return False

        self.video_translation_mode = bool(config.video_translation_mode)
        endpointing_ms = 600 if self.video_translation_mode else int(config.endpointing_ms)

        self.external_segmenter.configure(video_translation_mode=self.video_translation_mode)

        self.deepgram_external = DeepgramEngine(config.api_key, name="EXTERNAL")
        self.deepgram_external.text_received.connect(self._on_external_text)
        self.deepgram_external.connection_ready.connect(self._on_external_ready)
        self.deepgram_external.error.connect(self._on_service_log)

        if config.gemini_api_key:
            self.gemini_external = GeminiTranslator(
                config.gemini_api_key,
                is_voice_mode=False,
                is_auto_mic=False,
                is_video_mode=self.video_translation_mode,
                name="EXTERNAL",
                proxy_url=config.gemini_proxy_url,
            )
            self.gemini_external.set_target_lang(config.target_language_name)
            self.gemini_external.translation_ready.connect(self._on_external_translated)
            self.gemini_external.log_line.connect(self.log_line.emit)
        else:
            self.gemini_external = None
            self.log_line.emit("Ошибка: ключ Gemini пустой, перевод отключён", "error")

        self.system_audio = WindowsSystemAudioCapture(
            sample_rate=16000,
            frames_per_chunk=4096,
            speaker_id=config.system_device_id,
        )
        self.system_audio.signals.audio_chunk.connect(self._process_system_audio)
        self.system_audio.signals.level.connect(self.level_changed.emit)
        self.system_audio.signals.info.connect(self._on_system_log)
        self.system_audio.signals.error.connect(self._on_error_log)

        self.is_running = True
        self.started.emit()

        if self.video_translation_mode:
            self.log_line.emit(
                (
                    "SYS запущен: режим Видео перевода. "
                    f"Язык={config.language}, цель={config.target_language_name}, пауза=600 мс, "
                    "лимит фразы=без ограничений, OBS=без обрезки"
                ),
                "system",
            )
        else:
            self.log_line.emit(
                (
                    "SYS запущен: режим Realtime. "
                    f"Язык={config.language}, цель={config.target_language_name}, "
                    f"пауза={endpointing_ms} мс, лимит фразы=14 слов"
                ),
                "system",
            )

        self.deepgram_external.start(
            language=config.language,
            endpointing=endpointing_ms,
        )
        self.system_audio.start()
        return True

    def stop(self) -> None:
        if not self.is_running and not self.system_audio and not self.deepgram_external:
            return

        self.is_running = False

        if self.system_audio:
            self.system_audio.stop()
            self.system_audio = None

        if self.deepgram_external:
            self.deepgram_external.stop()
            self.deepgram_external = None

        if self.gemini_external:
            self.gemini_external.stop()
            self.gemini_external = None

        self.external_segmenter.reset()
        self.log_line.emit("SYS не запущен: звук системы не слушается", "system")
        self.level_changed.emit(0)
        self.stopped.emit()

    def toggle_microphone_recording(self, config: MicrophoneTranslationConfig) -> None:
        if not self._ensure_microphone_services(config):
            return

        if self.is_mic_recording:
            self._stop_manual_microphone_recording()
            return

        self._start_manual_microphone_recording()

    def stop_microphone_services(self) -> None:
        if self.is_mic_recording:
            self._stop_manual_microphone_recording(send_to_gemini=False)

        if self.microphone_audio:
            self.microphone_audio.stop()
            self.microphone_audio = None

        if self.deepgram_mic:
            self.deepgram_mic.stop()
            self.deepgram_mic = None

        if self.gemini_mic:
            self.gemini_mic.stop()
            self.gemini_mic = None

        self.microphone_runtime_signature = None
        self.mic_accumulated_text = ""
        self.is_mic_recording = False

    def _ensure_microphone_services(self, config: MicrophoneTranslationConfig) -> bool:
        recognition_language = str(config.recognition_language or "ru").strip() or "ru"
        endpointing_ms = int(config.endpointing_ms)
        runtime_signature = (
            recognition_language,
            endpointing_ms,
            str(config.microphone_device_id or ""),
            str(config.gemini_proxy_url or ""),
        )

        if self.microphone_audio and self.deepgram_mic and self.gemini_mic:
            self.gemini_mic.set_target_lang(config.target_language_name)
            self.gemini_mic.set_source_lang(config.recognition_language_name)
            self.gemini_mic.set_proxy_url(config.gemini_proxy_url)

            if self.is_mic_recording:
                return True

            if self.microphone_runtime_signature == runtime_signature:
                return True

            self.log_line.emit(
                (
                    "MIC: настройки распознавания изменились, "
                    f"перезапуск канала Deepgram на языке={recognition_language}"
                ),
                "system",
            )
            self.stop_microphone_services()

        if not config.api_key:
            self.log_line.emit("Ошибка MIC: ключ Deepgram пустой", "error")
            return False

        if not config.gemini_api_key:
            self.log_line.emit("Ошибка MIC: ключ Gemini пустой", "error")
            return False

        service_name = f"MIC-{recognition_language.upper()}"
        self.deepgram_mic = DeepgramEngine(config.api_key, name=service_name)
        self.deepgram_mic.text_received.connect(self._on_mic_text)
        self.deepgram_mic.connection_ready.connect(self._on_mic_ready)
        self.deepgram_mic.error.connect(self._on_service_log)

        self.gemini_mic = GeminiTranslator(
            config.gemini_api_key,
            is_voice_mode=True,
            is_auto_mic=False,
            is_video_mode=False,
            name=service_name,
            proxy_url=config.gemini_proxy_url,
        )
        self.gemini_mic.set_target_lang(config.target_language_name)
        self.gemini_mic.set_source_lang(config.recognition_language_name)
        self.gemini_mic.translation_ready.connect(self._on_mic_translated)
        self.gemini_mic.log_line.connect(self.log_line.emit)

        self.microphone_audio = WindowsMicrophoneCapture(
            sample_rate=16000,
            frames_per_chunk=4096,
            microphone_id=config.microphone_device_id,
        )
        self.microphone_audio.signals.audio_chunk.connect(self._process_microphone_audio)
        self.microphone_audio.signals.info.connect(self._on_system_log)
        self.microphone_audio.signals.error.connect(self._on_error_log)

        self.microphone_runtime_signature = runtime_signature

        self.log_line.emit(
            (
                "MIC сервис запускается: "
                f"Deepgram={recognition_language}, пауза={endpointing_ms} мс, "
                f"исходный язык={config.recognition_language_name}, "
                f"цель={config.target_language_name}"
            ),
            "system",
        )

        self.deepgram_mic.start(language=recognition_language, endpointing=endpointing_ms)
        self.microphone_audio.start()
        return True

    def _start_manual_microphone_recording(self) -> None:
        self.is_mic_recording = True
        self.mic_accumulated_text = ""

        if self.microphone_audio:
            self.microphone_audio.is_recording = True

        self.log_line.emit("MIC: запись включена. Говори фразу, потом нажми хоткей ещё раз", "system")
        self.microphone_recording_started.emit()
        self.microphone_transcription_changed.emit("Слушаю...")

    def _stop_manual_microphone_recording(self, *, send_to_gemini: bool = True) -> None:
        self.is_mic_recording = False

        if self.microphone_audio:
            self.microphone_audio.is_recording = False

        final_text = " ".join(self.mic_accumulated_text.split())
        self.mic_accumulated_text = ""
        self.microphone_recording_stopped.emit()

        if not send_to_gemini:
            return

        if not final_text:
            self.log_line.emit("MIC: запись остановлена, текста нет", "system")
            self.microphone_transcription_changed.emit("Ожидание голоса")
            return

        self.log_line.emit(f"Микрофон: {final_text}", "incoming")
        self.microphone_transcription_changed.emit(final_text)

        if self.gemini_mic:
            self.log_line.emit(f"MIC: фраза отправлена в Gemini, len={len(final_text)}", "system")
            self.gemini_mic.translate(final_text)

    def _process_system_audio(self, chunk_data, sample_rate: int) -> None:
        del sample_rate

        if not self.is_running or not self.deepgram_external:
            return

        amplified = np.clip(chunk_data * 3.0, -1.0, 1.0)
        audio_int16 = (amplified * 32767).astype(np.int16)
        self.deepgram_external.send_audio(audio_int16.tobytes())

    def _process_microphone_audio(self, chunk_data, sample_rate: int) -> None:
        del sample_rate

        if not self.is_mic_recording or not self.deepgram_mic:
            return

        amplified = np.clip(chunk_data * 2.0, -1.0, 1.0)
        audio_int16 = (amplified * 32767).astype(np.int16)
        self.deepgram_mic.send_audio(audio_int16.tobytes())

    def _on_external_ready(self) -> None:
        self.log_line.emit("Канал Deepgram для внешних голосов готов", "system")
        self.ready.emit()

    def _on_mic_ready(self) -> None:
        self.log_line.emit("Канал Deepgram для микрофона готов", "system")

    def _on_external_text(self, text: str, is_final: bool, speech_final: bool) -> None:
        clean = " ".join(str(text or "").split())
        if not clean:
            return

        segments = self.external_segmenter.push(
            clean,
            is_final=is_final,
            speech_final=speech_final,
        )
        if not segments:
            return

        if not is_final and not self.video_translation_mode:
            self.log_line.emit(
                f"Ранний перевод: фраза разбита до финального пакета Deepgram, частей={len(segments)}",
                "system",
            )

        for segment in segments:
            self.log_line.emit(f"Внешние голоса: {segment}", "incoming")
            self.incoming_text.emit(segment)

            if self.gemini_external:
                self.gemini_external.translate(segment)

    def _on_mic_text(self, text: str, is_final: bool, speech_final: bool) -> None:
        del speech_final

        if not self.is_mic_recording:
            return

        clean = " ".join(str(text or "").split())
        if not clean:
            return

        if not is_final:
            self.microphone_transcription_changed.emit(clean)
            return

        if self.mic_accumulated_text:
            self.mic_accumulated_text = f"{self.mic_accumulated_text} {clean}"
        else:
            self.mic_accumulated_text = clean

        self.microphone_transcription_changed.emit(self.mic_accumulated_text)

    def _on_external_translated(self, original: str, translated: str) -> None:
        clean_translation = " ".join(str(translated or "").split())
        if not clean_translation:
            return

        self.log_line.emit(f"Перевод: {clean_translation}", "translation")
        self.translation_ready.emit(str(original or "").strip(), clean_translation)

    def _on_mic_translated(self, original: str, translated: str) -> None:
        clean_translation = " ".join(str(translated or "").split())
        if not clean_translation:
            return

        self.log_line.emit(f"Перевод микрофона: {clean_translation}", "translation")
        self.microphone_translation_ready.emit(str(original or "").strip(), clean_translation)

    def _on_system_log(self, line: str) -> None:
        self.log_line.emit(str(line), "system")

    def _on_error_log(self, line: str) -> None:
        self.log_line.emit(str(line), "error")

    def _on_service_log(self, line: str) -> None:
        category = "error" if self._looks_like_error(line) else "system"
        self.log_line.emit(str(line), category)

    def _looks_like_error(self, line: str) -> bool:
        lowered = str(line).lower()
        return any(
            marker in lowered
            for marker in (
                "ошибка",
                "не удалось",
                "не хватает",
                "пуст",
                "потерян",
                "не прош",
                "закрыто",
                "failed",
                "error",
                "empty",
            )
        )