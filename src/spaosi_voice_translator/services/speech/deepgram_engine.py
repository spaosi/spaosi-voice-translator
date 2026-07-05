from __future__ import annotations

import logging
import os
import queue
import threading
import time
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal


def quiet_noisy_deepgram_console_logs() -> None:
    """Reduce noisy Deepgram/WebSocket console output on abnormal closes.

    The app already shows controlled reconnect errors in its own log panel. Some
    versions of deepgram-sdk also write raw ConnectionClosed traces to stderr.
    Those traces confuse users and duplicate the app log, so keep third-party
    loggers quiet.
    """

    for logger_name in (
        "deepgram",
        "deepgram.clients",
        "websocket",
        "websockets",
        "websockets.client",
        "AbstractSyncWebSocketClient",
    ):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)
        logger.propagate = False


class DeepgramEngine(QObject):
    text_received = pyqtSignal(str, bool, bool)
    connection_ready = pyqtSignal()
    closed = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, api_key: str, *, name: str = "Deepgram"):
        super().__init__()
        self.api_key = api_key
        self.name = name
        self.language = "en"
        self.endpointing = 300

        self._active = False
        self._connected = False
        self._audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=100)
        self._connection = None
        self._send_thread: threading.Thread | None = None
        self._connect_thread: threading.Thread | None = None
        self._reconnect_thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._reconnect_attempt = 0
        self._reconnecting = False
        self._max_reconnect_attempts = 8

    def start(self, *, language: str = "en", endpointing: int = 300) -> None:
        with self._lock:
            if self._active:
                return

            self.language = self._normalize_language(language)
            self.endpointing = int(endpointing)
            self._active = True
            self._connected = False
            self._reconnect_attempt = 0
            self._reconnecting = False

        self._drain_queue()
        quiet_noisy_deepgram_console_logs()
        self._prepare_tls_environment()
        self.error.emit(
            f"Deepgram[{self.name}]: подключение, язык={self.language}, пауза={endpointing} мс"
        )

        self._connect_thread = threading.Thread(target=self._connect, daemon=True)
        self._connect_thread.start()

        self._send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self._send_thread.start()

    def send_audio(self, audio_bytes: bytes) -> None:
        with self._lock:
            can_send = self._active and self._connected and self._connection is not None

        if not can_send:
            return

        try:
            self._audio_queue.put_nowait(audio_bytes)
        except queue.Full:
            pass

    def stop(self) -> None:
        with self._lock:
            self._active = False
            self._connected = False
            self._reconnecting = False
            connection = self._connection
            self._connection = None

        self._drain_queue()

        if connection is not None:
            threading.Thread(target=self._finish_connection, args=(connection,), daemon=True).start()

        self.closed.emit()
        self.error.emit(f"Deepgram[{self.name}]: канал остановлен")

    def _normalize_language(self, language: str) -> str:
        clean = str(language or "").strip()
        return clean or "en"

    def _prepare_tls_environment(self) -> None:
        """Keep Deepgram WebSocket startup stable on Windows virtual environments.

        Some Windows shells keep SSL_CERT_FILE / REQUESTS_CA_BUNDLE pointing to a
        deleted certificate bundle. The Deepgram WebSocket client then fails with
        FileNotFoundError before audio is sent. We remove broken paths and point
        Python SSL to certifi when it is installed.
        """

        for env_key in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
            value = os.environ.get(env_key, "").strip()
            if value and not Path(value).is_file():
                os.environ.pop(env_key, None)

        if os.environ.get("SSL_CERT_FILE") and Path(os.environ["SSL_CERT_FILE"]).is_file():
            return

        try:
            import certifi
        except ImportError:
            return

        cert_file = Path(certifi.where())
        if cert_file.is_file():
            os.environ.setdefault("SSL_CERT_FILE", str(cert_file))
            os.environ.setdefault("REQUESTS_CA_BUNDLE", str(cert_file))

    def _connect(self) -> None:
        try:
            from deepgram import (
                DeepgramClient,
                DeepgramClientOptions,
                LiveOptions,
                LiveTranscriptionEvents,
            )
        except ImportError as exc:
            self.error.emit(
                "Ошибка Deepgram: не хватает deepgram-sdk. "
                "Установи зависимости через pip install -e ."
            )
            self.error.emit(str(exc))
            with self._lock:
                self._active = False
                self._connected = False
            return

        try:
            self._prepare_tls_environment()
            config = DeepgramClientOptions(options={"keepalive": "true"})
            client = DeepgramClient(self.api_key, config)
            connection = client.listen.live.v("1")

            options = LiveOptions(
                model="nova-3",
                language=self.language,
                smart_format=True,
                interim_results=True,
                encoding="linear16",
                channels=1,
                sample_rate=16000,
                endpointing=self.endpointing,
            )

            def on_message(_client, result, **_kwargs) -> None:
                with self._lock:
                    active = self._active

                if not active:
                    return

                try:
                    transcript = result.channel.alternatives[0].transcript
                    speech_final = bool(getattr(result, "speech_final", False))
                    is_final = bool(getattr(result, "is_final", False))
                except Exception:
                    return

                if transcript or speech_final:
                    self.text_received.emit(transcript, is_final, speech_final)

            def on_error(_client, error, **_kwargs) -> None:
                self.error.emit(f"Ошибка Deepgram: {error}")
                self._schedule_reconnect("WebSocket error")

            def on_close(_client, close, **_kwargs) -> None:
                close_text = str(close or "").strip()

                with self._lock:
                    was_active = self._active
                    self._connected = False
                    self._connection = None

                if was_active:
                    reason = f"WebSocket closed: {close_text}" if close_text else "WebSocket closed"
                    self.error.emit(f"Ошибка Deepgram[{self.name}]: соединение закрыто, переподключение")
                    self._schedule_reconnect(reason)

            connection.on(LiveTranscriptionEvents.Transcript, on_message)
            connection.on(LiveTranscriptionEvents.Error, on_error)

            if hasattr(LiveTranscriptionEvents, "Close"):
                connection.on(LiveTranscriptionEvents.Close, on_close)

            started_at = time.perf_counter()
            connection.start(options)
            start_ms = int((time.perf_counter() - started_at) * 1000)

            with self._lock:
                if not self._active:
                    self._finish_connection(connection)
                    return

                self._connection = connection
                self._connected = True
                self._reconnect_attempt = 0

            self.error.emit(f"Deepgram[{self.name}]: подключение установлено за {start_ms} мс")
            self.connection_ready.emit()

        except FileNotFoundError as exc:
            self.error.emit(
                "Ошибка Deepgram: WebSocket не смог найти SSL/cert файл. "
                "Проверь обновление зависимостей через pip install -e ."
            )
            self.error.emit(f"Deepgram[{self.name}]: {exc}")
            with self._lock:
                self._active = False
                self._connected = False
                self._connection = None

        except Exception as exc:
            self.error.emit(f"Ошибка Deepgram[{self.name}]: не удалось подключиться: {exc}")
            with self._lock:
                active = self._active
                self._connected = False
                self._connection = None

            if active:
                self._schedule_reconnect(f"connect failed: {exc}")

    def _schedule_reconnect(self, reason: str) -> None:
        with self._lock:
            if not self._active:
                return

            connection = self._connection
            self._connection = None
            self._connected = False

            if self._reconnecting:
                return

            self._reconnect_attempt += 1
            attempt = self._reconnect_attempt

            if attempt > self._max_reconnect_attempts:
                self._active = False
                self._reconnecting = False
                self.error.emit(
                    f"Ошибка Deepgram[{self.name}]: переподключение остановлено после {self._max_reconnect_attempts} попыток"
                )
                return

            self._reconnecting = True

        if connection is not None:
            threading.Thread(target=self._finish_connection, args=(connection,), daemon=True).start()

        delay_seconds = min(1.0 + attempt * 0.75, 6.0)
        self.error.emit(
            f"Deepgram[{self.name}]: WebSocket потерян ({reason}), попытка {attempt}/{self._max_reconnect_attempts} через {delay_seconds:.1f} сек"
        )

        def reconnect_later() -> None:
            time.sleep(delay_seconds)

            with self._lock:
                if not self._active:
                    self._reconnecting = False
                    return

                self._reconnecting = False

            self._connect()

        self._reconnect_thread = threading.Thread(target=reconnect_later, daemon=True)
        self._reconnect_thread.start()

    def _send_loop(self) -> None:
        empty_ticks = 0

        while True:
            with self._lock:
                active = self._active
                connected = self._connected
                connection = self._connection

            if not active:
                return

            if not connected or connection is None:
                time.sleep(0.05)
                continue

            try:
                chunk = self._audio_queue.get(timeout=0.1)
                connection.send(chunk)
                empty_ticks = 0

            except queue.Empty:
                empty_ticks += 1
                if empty_ticks >= 40:
                    try:
                        connection.send(b"\x00" * 8192)
                    except Exception as exc:
                        self.error.emit(f"Ошибка Deepgram: keepalive не прошел: {exc}")
                        self._schedule_reconnect(f"keepalive failed: {exc}")
                    empty_ticks = 0

            except Exception as exc:
                self.error.emit(f"Ошибка Deepgram: отправка аудио не удалась: {exc}")
                self._schedule_reconnect(f"send failed: {exc}")
                time.sleep(0.2)

    def _finish_connection(self, connection) -> None:
        try:
            connection.finish()
        except Exception:
            pass

    def _drain_queue(self) -> None:
        try:
            while True:
                self._audio_queue.get_nowait()
        except queue.Empty:
            pass
