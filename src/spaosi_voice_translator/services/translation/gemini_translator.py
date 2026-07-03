from __future__ import annotations

import queue
import re
import threading
import time
from collections import deque

from PyQt6.QtCore import QObject, pyqtSignal

from spaosi_voice_translator.services.translation.prompts import build_prompt


DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com"


class GeminiTranslator(QObject):
    translation_ready = pyqtSignal(str, str)
    log_line = pyqtSignal(str, str)

    def __init__(
        self,
        api_key: str,
        *,
        is_voice_mode: bool = False,
        is_auto_mic: bool = False,
        is_video_mode: bool = False,
        name: str = "GAME",
        proxy_url: str = "",
    ):
        super().__init__()
        self.api_key = api_key
        self.proxy_url = self._normalize_proxy_url(proxy_url)
        self.model_name = "gemini-3.1-flash-lite"
        self.is_voice_mode = is_voice_mode
        self.is_auto_mic = is_auto_mic
        self.is_video_mode = is_video_mode
        self.name = name
        self.target_lang = "Английский"
        self.source_lang = "Auto"

        self.task_queue: queue.Queue[tuple[int, str, float, str]] = queue.Queue(maxsize=20)
        self.history = deque(maxlen=4)
        self.recent_outputs = deque(maxlen=5)
        self.last_translated_text = ""
        self.pending_text = ""

        self._lock = threading.RLock()
        self._generation = 0
        self._is_running = True

        self._session = None
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def translate(self, text: str, trace_id: str | None = None) -> None:
        clean_text = str(text or "").strip()
        if len(clean_text) <= 1:
            return

        with self._lock:
            if not self._is_running:
                return
            generation = self._generation

        try:
            self.task_queue.put_nowait(
                (generation, clean_text, time.perf_counter(), str(trace_id or ""))
            )
            self.log_line.emit(
                f"Gemini[{self.name}]: фраза добавлена в очередь, длина={len(clean_text)}",
                "system",
            )
        except queue.Full:
            self.log_line.emit(
                f"Ошибка Gemini[{self.name}]: очередь перевода заполнена, фраза пропущена",
                "error",
            )

    def set_target_lang(self, lang_name: str) -> None:
        self.target_lang = str(lang_name or "Английский").strip() or "Английский"

    def set_source_lang(self, lang_name: str) -> None:
        self.source_lang = str(lang_name or "Auto").strip() or "Auto"

    def set_proxy_url(self, proxy_url: str) -> None:
        self.proxy_url = self._normalize_proxy_url(proxy_url)

    def _normalize_proxy_url(self, proxy_url: str) -> str:
        clean = str(proxy_url or "").strip().rstrip("/")
        if clean and not clean.startswith(("http://", "https://")):
            clean = f"http://{clean}"
        return clean

    def _api_base_url(self) -> str:
        return self.proxy_url or DEFAULT_GEMINI_BASE_URL

    def _build_request_url_and_headers(self) -> tuple[str, dict[str, str]]:
        base_url = self._api_base_url()
        headers = {"Content-Type": "application/json"}

        if self.proxy_url:
            return (
                f"{base_url}/v1beta/models/{self.model_name}:generateContent?key={self.api_key}",
                headers,
            )

        headers["x-goog-api-key"] = self.api_key
        return f"{base_url}/v1beta/models/{self.model_name}:generateContent", headers

    def _response_error_details(self, response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                error = data.get("error")
                if isinstance(error, dict):
                    message = str(error.get("message") or "").strip()
                    status = str(error.get("status") or "").strip()
                    if status and message:
                        return f"{status}: {message}"
                    return message or status
        except Exception:
            pass

        try:
            text = str(response.text or "").strip()
        except Exception:
            return ""

        text = re.sub(r"\s+", " ", text)
        if len(text) > 260:
            text = text[:257].rstrip() + "..."
        return text

    def cancel_pending(self) -> None:
        with self._lock:
            self._generation += 1
            self.pending_text = ""
            self.last_translated_text = ""
            self.recent_outputs.clear()

        drained = 0
        try:
            while True:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
                drained += 1
        except queue.Empty:
            pass

        if drained:
            self.log_line.emit(f"Gemini[{self.name}]: очищено ожидающих переводов: {drained}", "system")

    def stop(self) -> None:
        self.cancel_pending()

        with self._lock:
            self._is_running = False
            self._generation += 1

        if self._session is not None:
            try:
                self._session.close()
            except Exception:
                pass
            self._session = None

        self.log_line.emit(f"Gemini[{self.name}]: остановлен", "system")

    def _process_queue(self) -> None:
        while True:
            with self._lock:
                running = self._is_running

            if not running:
                return

            try:
                generation, text_to_translate, queued_at, trace_id = self.task_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            try:
                if not self._is_generation_current(generation):
                    continue

                queue_wait_ms = int((time.perf_counter() - queued_at) * 1000)
                self.log_line.emit(
                    f"Gemini[{self.name}]: взял фразу из очереди за {queue_wait_ms} мс",
                    "system",
                )

                self._translate_now(generation, text_to_translate, trace_id)

            finally:
                try:
                    self.task_queue.task_done()
                except Exception:
                    pass

    def _translate_now(self, generation: int, target_text: str, trace_id: str) -> None:
        if not self.api_key:
            self.log_line.emit("Ошибка Gemini: ключ Gemini пустой, перевод отключён", "error")
            return

        current_target = str(target_text or "").strip()
        if not current_target:
            return

        if self.is_auto_mic and self._is_really_russian(current_target):
            self.log_line.emit(f"Gemini[{self.name}]: авто-фильтр, русский текст пропущен", "system")
            return

        force_translate_note = ""
        if len(current_target) > 100:
            if self.is_video_mode:
                force_translate_note = (
                    "\n\n[СИСТЕМНОЕ ТРЕБОВАНИЕ: Текста много. "
                    "Переведи всю целевую фразу целиком, без сокращения и без WAIT.]"
                )
            else:
                force_translate_note = (
                    "\n\n[СИСТЕМНОЕ ТРЕБОВАНИЕ: Текста много! "
                    "ПЕРЕВЕДИ СЕЙЧАС ЖЕ, запрещено использовать WAIT!]"
                )

        prompt = build_prompt(
            target_text=current_target,
            force_translate_note=force_translate_note,
            is_voice_mode=self.is_voice_mode,
            is_auto_mic=self.is_auto_mic,
            is_video_mode=self.is_video_mode,
            target_lang=self.target_lang,
            source_lang=self.source_lang,
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": self._temperature()},
        }

        if self.proxy_url:
            payload["safetySettings"] = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

        url, headers = self._build_request_url_and_headers()

        started_at = time.perf_counter()

        try:
            response = self._requests_session().post(
                url,
                headers=headers,
                json=payload,
                timeout=8 if self.is_video_mode else 6,
            )
        except Exception as exc:
            self.log_line.emit(f"Ошибка Gemini[{self.name}]: запрос не удался: {exc}", "error")
            return

        elapsed_ms = int((time.perf_counter() - started_at) * 1000)

        if not self._is_generation_current(generation):
            return

        if response.status_code != 200:
            details = self._response_error_details(response)
            suffix = f": {details}" if details else ""
            self.log_line.emit(
                f"Ошибка Gemini[{self.name}]: HTTP {response.status_code}{suffix}",
                "error",
            )
            return

        try:
            data = response.json()
            translated_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as exc:
            self.log_line.emit(f"Ошибка Gemini[{self.name}]: не удалось прочитать ответ: {exc}", "error")
            return

        translated_text = self._clean_model_output(translated_text)

        if not translated_text:
            self.log_line.emit(f"Gemini[{self.name}]: пустой ответ модели", "system")
            return

        if translated_text.upper() == "WAIT":
            self.log_line.emit(f"Gemini[{self.name}]: WAIT, фрагмент пропущен", "system")
            return

        if self._is_repeated_output(translated_text):
            self.log_line.emit(f"Gemini[{self.name}]: повтор перевода пропущен", "system")
            return

        self.last_translated_text = translated_text
        self.recent_outputs.append(translated_text)
        self.history.append(current_target)

        trace_suffix = f", trace={trace_id}" if trace_id else ""
        self.log_line.emit(
            f"Gemini[{self.name}]: перевод готов за {elapsed_ms} мс{trace_suffix}",
            "system",
        )
        self.translation_ready.emit(current_target, translated_text)

    def _requests_session(self):
        if self._session is None:
            import requests

            self._session = requests.Session()

        return self._session

    def _temperature(self) -> float:
        if self.is_voice_mode:
            return 0.25
        if self.is_auto_mic:
            return 0.25
        if self.is_video_mode:
            return 0.35
        return 0.35

    def _clean_model_output(self, text: str) -> str:
        text = str(text or "").strip()
        text = re.sub(r"^```(?:text|markdown)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()
        text = text.replace("…", "...")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _normalize_for_repeat(self, text: str) -> str:
        text = str(text or "").lower().replace("ё", "е")
        text = re.sub(r"[^a-zа-я0-9\s]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _is_repeated_output(self, translated_text: str) -> bool:
        norm = self._normalize_for_repeat(translated_text)
        if not norm:
            return False

        last_norm = self._normalize_for_repeat(self.last_translated_text)
        if norm == last_norm:
            return True

        for recent in self.recent_outputs:
            recent_norm = self._normalize_for_repeat(recent)
            if norm == recent_norm:
                return True

        return False

    def _is_really_russian(self, text: str) -> bool:
        clean = str(text or "").strip()
        if not clean:
            return False

        cyrillic = len(re.findall(r"[А-Яа-яЁё]", clean))
        latin = len(re.findall(r"[A-Za-z]", clean))
        return cyrillic >= 3 and cyrillic > latin

    def _is_generation_current(self, generation: int) -> bool:
        with self._lock:
            return self._is_running and self._generation == generation
