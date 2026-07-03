from __future__ import annotations

import time
import warnings

from PyQt6.QtCore import QObject, QThread, pyqtSignal

warnings.filterwarnings("ignore", message=r".*data discontinuity in recording.*")


def _suppress_soundcard_warnings() -> None:
    warnings.filterwarnings("ignore", message=r".*data discontinuity in recording.*")

    try:
        from soundcard.mediafoundation import SoundcardRuntimeWarning

        warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)
    except Exception:
        pass


class AudioCaptureSignals(QObject):
    audio_chunk = pyqtSignal(object, int)
    level = pyqtSignal(int)
    info = pyqtSignal(str)
    error = pyqtSignal(str)


class WindowsSystemAudioCapture(QThread):
    """System audio capture through WASAPI loopback."""

    def __init__(
        self,
        *,
        sample_rate: int = 16000,
        frames_per_chunk: int = 4096,
        speaker_id: str = "",
    ):
        super().__init__()
        self.signals = AudioCaptureSignals()
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.speaker_id = speaker_id
        self._is_running = False

    def run(self) -> None:
        _suppress_soundcard_warnings()

        try:
            import numpy as np
            import soundcard as sc

            _suppress_soundcard_warnings()
        except ImportError as exc:
            self.signals.error.emit(
                "Ошибка Windows Audio API: не хватает зависимости. "
                "Установи зависимости через pip install -e ."
            )
            self.signals.error.emit(str(exc))
            return

        self._is_running = True

        while self._is_running:
            try:
                speaker = self._resolve_speaker(sc)
                loopback = sc.get_microphone(speaker.id, include_loopback=True)
                self.signals.info.emit(f"Захват системного звука: {speaker.name}")

                with loopback.recorder(samplerate=self.sample_rate) as recorder:
                    while self._is_running:
                        with warnings.catch_warnings():
                            _suppress_soundcard_warnings()
                            data = recorder.record(numframes=self.frames_per_chunk)

                        if data is None or len(data) == 0:
                            continue

                        if len(data.shape) > 1:
                            data = data.mean(axis=1)

                        data = np.asarray(data, dtype=np.float32)
                        rms = float(np.sqrt(np.mean(np.square(data)))) if len(data) else 0.0
                        self.signals.level.emit(int(min(rms * 320, 100)))
                        self.signals.audio_chunk.emit(data, self.sample_rate)

            except Exception as exc:
                if not self._is_running:
                    break

                self.signals.error.emit(f"Ошибка Windows Audio API: захват звука потерян: {exc}")
                time.sleep(2.0)

    def stop(self) -> None:
        self._is_running = False
        self.wait(1500)

    def _resolve_speaker(self, sc):
        if not self.speaker_id:
            return sc.default_speaker()

        for speaker in sc.all_speakers():
            if str(getattr(speaker, "id", "")) == self.speaker_id:
                return speaker

        self.signals.error.emit("Ошибка Windows Audio API: выбранное устройство не найдено, используется стандартное")
        return sc.default_speaker()


class WindowsMicrophoneCapture(QThread):
    """Microphone capture for manual hotkey translation.

    The thread keeps the microphone recorder alive, but emits audio only while
    is_recording=True. This makes the first hotkey cycle usable and avoids
    recreating the audio device after every phrase.
    """

    def __init__(
        self,
        *,
        sample_rate: int = 16000,
        frames_per_chunk: int = 4096,
        microphone_id: str = "",
    ):
        super().__init__()
        self.signals = AudioCaptureSignals()
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.microphone_id = microphone_id
        self.is_recording = False
        self._is_running = False

    def run(self) -> None:
        _suppress_soundcard_warnings()

        try:
            import numpy as np
            import soundcard as sc

            _suppress_soundcard_warnings()
        except ImportError as exc:
            self.signals.error.emit(
                "Ошибка Windows Audio API: не хватает зависимости. "
                "Установи зависимости через pip install -e ."
            )
            self.signals.error.emit(str(exc))
            return

        self._is_running = True

        while self._is_running:
            try:
                microphone = self._resolve_microphone(sc)
                self.signals.info.emit(f"Захват микрофона: {microphone.name}")

                with microphone.recorder(samplerate=self.sample_rate) as recorder:
                    while self._is_running:
                        with warnings.catch_warnings():
                            _suppress_soundcard_warnings()
                            data = recorder.record(numframes=self.frames_per_chunk)

                        if data is None or len(data) == 0:
                            continue

                        if len(data.shape) > 1:
                            data = data.mean(axis=1)

                        data = np.asarray(data, dtype=np.float32)
                        rms = float(np.sqrt(np.mean(np.square(data)))) if len(data) else 0.0

                        if self.is_recording:
                            self.signals.level.emit(int(min(rms * 360, 100)))
                            self.signals.audio_chunk.emit(data, self.sample_rate)

            except Exception as exc:
                if not self._is_running:
                    break

                self.signals.error.emit(f"Ошибка Windows Audio API: захват микрофона потерян: {exc}")
                time.sleep(2.0)

    def stop(self) -> None:
        self.is_recording = False
        self._is_running = False
        self.wait(1500)

    def _resolve_microphone(self, sc):
        if not self.microphone_id:
            return sc.default_microphone()

        for microphone in sc.all_microphones(include_loopback=False):
            if str(getattr(microphone, "id", "")) == self.microphone_id:
                return microphone

        self.signals.error.emit("Ошибка Windows Audio API: выбранный микрофон не найден, используется стандартный")
        return sc.default_microphone()
