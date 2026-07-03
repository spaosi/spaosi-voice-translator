from __future__ import annotations

import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

MESSAGE_HISTORY: list[dict] = []
MSG_ID = 0
LAST_UPDATE_TIME = 0.0
SINGLE_WORD_BUFFER: list[str] = []
RECENT_OBS_TEXTS: list[str] = []
MAX_OBS_HISTORY = 2

OBS_SERVER_STARTED = False
OBS_SERVER_ERROR: str | None = None
OBS_SERVER_URL = "http://127.0.0.1:8088/obs"
_HTTP_SERVER: ThreadingHTTPServer | None = None


class OBSWidgetHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        clean_path = urlparse(self.path).path.rstrip("/") or "/"

        if clean_path == "/api/text":
            self._send_json({"messages": MESSAGE_HISTORY})
            return

        if clean_path in {"/", "/obs"}:
            self._send_html(_obs_html())
            return

        self.send_error(404)

    def _send_json(self, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_obs_server(port: int = 8088) -> str:
    global OBS_SERVER_STARTED, OBS_SERVER_ERROR, OBS_SERVER_URL, _HTTP_SERVER

    if OBS_SERVER_STARTED and _HTTP_SERVER is not None:
        return OBS_SERVER_URL

    OBS_SERVER_URL = f"http://127.0.0.1:{int(port)}/obs"

    def run() -> None:
        global OBS_SERVER_STARTED, OBS_SERVER_ERROR, _HTTP_SERVER

        try:
            _HTTP_SERVER = ThreadingHTTPServer(("127.0.0.1", int(port)), OBSWidgetHandler)
            OBS_SERVER_STARTED = True
            OBS_SERVER_ERROR = None
            _HTTP_SERVER.serve_forever()
        except Exception as exc:
            OBS_SERVER_STARTED = False
            OBS_SERVER_ERROR = str(exc)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    time.sleep(0.05)
    return OBS_SERVER_URL


def obs_status() -> tuple[bool, str | None, str]:
    return OBS_SERVER_STARTED, OBS_SERVER_ERROR, OBS_SERVER_URL


def clear_obs_text() -> None:
    global MSG_ID, LAST_UPDATE_TIME
    MESSAGE_HISTORY.clear()
    SINGLE_WORD_BUFFER.clear()
    RECENT_OBS_TEXTS.clear()
    LAST_UPDATE_TIME = 0.0
    MSG_ID += 1


def set_obs_text(
    text: str,
    *,
    is_mic: bool = False,
    mic_prefix: bool = True,
    max_chars: int | None = None,
) -> dict:
    """Send text to OBS.

    max_chars=None keeps the old Horizont behavior.
    max_chars=0 disables OBS trimming completely. Used by video translation mode.
    """

    global MSG_ID, LAST_UPDATE_TIME

    if not text:
        return _obs_result(False, "empty_input")

    if is_mic:
        text = strip_voice_transcription(text)

    text = text.replace("WAIT", "").strip()
    if not text:
        return _obs_result(False, "wait_or_empty_after_clean")

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = remove_duplicates(text)
    text = remove_repeated_sentences(text)
    text = polish_subtitle_punctuation(text)
    if not text:
        return _obs_result(False, "empty_after_polish")

    SINGLE_WORD_BUFFER.clear()

    if max_chars == 0:
        text_to_show = text
    else:
        effective_max_chars = max_chars if max_chars is not None else (72 if is_mic else 78)
        text_to_show = beautiful_cut(text, max_chars=effective_max_chars)

    text_to_show = polish_subtitle_punctuation(text_to_show)
    if not text_to_show:
        return _obs_result(False, "empty_after_cut")

    current_time = time.time()
    if current_time - LAST_UPDATE_TIME > 7:
        MESSAGE_HISTORY.clear()
        SINGLE_WORD_BUFFER.clear()

    if is_too_similar_to_last(text_to_show):
        return _obs_result(False, "too_similar_to_previous", text_to_show)

    if is_mic and mic_prefix:
        text_to_show = f"[Я]: {text_to_show}"

    LAST_UPDATE_TIME = current_time
    MSG_ID += 1

    MESSAGE_HISTORY.append({"id": MSG_ID, "text": text_to_show, "is_mic": is_mic})
    RECENT_OBS_TEXTS.append(text_to_show)
    if len(RECENT_OBS_TEXTS) > 8:
        RECENT_OBS_TEXTS.pop(0)

    if len(MESSAGE_HISTORY) > MAX_OBS_HISTORY:
        del MESSAGE_HISTORY[:-MAX_OBS_HISTORY]

    return _obs_result(True, "ok", text_to_show)


def remove_duplicates(text: str) -> str:
    words = text.split()
    if not words:
        return text

    result = [words[0]]
    for i in range(1, len(words)):
        prev_clean = re.sub(r"[^\w]", "", result[-1]).lower()
        curr_clean = re.sub(r"[^\w]", "", words[i]).lower()
        if curr_clean != prev_clean or curr_clean == "":
            result.append(words[i])

    return " ".join(result)


def beautiful_cut(text: str, max_chars: int = 86) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text

    cut_pos = text.rfind(" ", 0, max_chars)
    if cut_pos < max_chars * 0.55:
        cut_pos = max_chars

    return text[:cut_pos].rstrip(".,!?;:") + "..."


def strip_voice_transcription(text: str) -> str:
    text = (text or "").strip()
    match = re.match(r"^(.*?)\s*\[([^\[\]]+)\]\s*$", text)
    if not match:
        return text

    translation = match.group(1).strip()
    pronunciation_guide = match.group(2).strip()

    if not translation or not pronunciation_guide:
        return text

    # MIC output uses trailing brackets for a pronunciation guide. The guide can be
    # Cyrillic, Latin, or another script depending on the speaker's source language.
    # OBS subtitles should show only the clean translation.
    return translation


def normalize_for_repeat(text: str) -> str:
    text = (text or "").lower().replace("ё", "е")
    text = re.sub(r"[^a-zа-я0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def remove_repeated_sentences(text: str) -> str:
    parts = [p.strip() for p in re.split(r"(?<=[.!?…])\s+", text) if p.strip()]
    if len(parts) <= 1:
        return text

    result: list[str] = []
    seen: set[str] = set()

    for part in parts:
        norm = normalize_for_repeat(part)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        result.append(part)

    return " ".join(result)


def polish_subtitle_punctuation(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return ""

    text = text.replace("…", "...")
    text = re.sub(r"\.{4,}", "...", text)

    dot_parts = [p.strip() for p in re.split(r"(?<!\.)\.\s+", text) if p.strip()]
    if len(dot_parts) > 1:
        word_counts = [len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", p)) for p in dot_parts]
        if sum(word_counts) <= 10 and max(word_counts) <= 5:
            cleaned_parts = []
            for idx, part in enumerate(dot_parts):
                part = part.rstrip(" .")
                if idx > 0:
                    part = _lowercase_first_letter(part)
                cleaned_parts.append(part)
            text = ", ".join(p for p in cleaned_parts if p.strip())

    if text.endswith(".") and not text.endswith("..."):
        text = text[:-1].rstrip()

    text = re.sub(r"\s+([,!?])", r"\1", text)
    text = re.sub(r",\s*,+", ", ", text)
    return text.strip()


def _lowercase_first_letter(text: str) -> str:
    if not text:
        return text

    match = re.search(r"[А-ЯЁA-Z]", text)
    if not match:
        return text

    index = match.start()
    token = re.match(r"[A-ZА-ЯЁ]{2,}\b", text[index:])
    if token:
        return text

    return text[:index] + text[index].lower() + text[index + 1 :]


def is_too_similar_to_last(text: str) -> bool:
    norm_text = normalize_for_repeat(text)
    if not norm_text:
        return False

    candidates: list[str] = []
    if MESSAGE_HISTORY:
        candidates.append(str(MESSAGE_HISTORY[-1].get("text", "")))
    candidates.extend(RECENT_OBS_TEXTS[-4:])

    words_text = set(norm_text.split())

    for previous in candidates:
        norm_previous = normalize_for_repeat(previous)
        if not norm_previous:
            continue

        if norm_text == norm_previous:
            return True

        words_previous = set(norm_previous.split())
        if len(words_text) < 3 or len(words_previous) < 3:
            continue

        overlap = len(words_text & words_previous) / max(1, min(len(words_text), len(words_previous)))
        if overlap >= 0.78:
            return True

        if len(norm_text) > 18 and (norm_text in norm_previous or norm_previous in norm_text):
            return True

    return False


def _obs_result(shown: bool, reason: str = "ok", text: str = "") -> dict:
    return {"shown": bool(shown), "reason": reason, "text": text}


def _obs_html() -> str:
    return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0; padding: 0 40px 50px 40px; background-color: transparent;
            font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
            text-align: center; display: flex; flex-direction: column;
            justify-content: flex-end; align-items: center; height: 100vh;
            box-sizing: border-box; overflow: hidden;
        }
        #container {
            display: flex; flex-direction: column; align-items: center;
            gap: 12px; transition: opacity 0.5s ease-in-out;
            width: 100%; max-width: 1300px;
        }
        .message {
            background: transparent; border: none;
            font-size: 34px; font-weight: 700; line-height: 1.3;
            text-shadow:
                -2px -2px 0 #000, 2px -2px 0 #000,
                -2px 2px 0 #000, 2px 2px 0 #000,
                0px 4px 12px rgba(0,0,0,0.9);
            animation: fadeIn 0.4s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            word-wrap: break-word;
            overflow-wrap: anywhere;
        }
        .message.game { color: #FFFDE7; }
        .message.mic { color: #00FFFF; font-weight: 900; }
        .message.secondary {
            opacity: 0.48;
            font-size: 27px;
            transform: translateY(-2px) scale(0.96);
            transition: all 0.4s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .hidden { opacity: 0 !important; }
    </style>
</head>
<body>
    <div id="container" class="hidden"></div>
    <script>
        const container = document.getElementById('container');
        let currentIds = "";
        let hideTimeout = null;

        function renderMessages(messages) {
            container.innerHTML = '';
            messages.forEach((msg, index) => {
                const div = document.createElement('div');
                div.innerText = msg.text;

                let cls = 'message';
                if (msg.is_mic) cls += ' mic';
                else cls += ' game';

                if (index !== messages.length - 1) cls += ' secondary';
                div.className = cls;

                container.appendChild(div);
            });
        }

        setInterval(() => {
            fetch('/api/text?ts=' + Date.now(), { cache: 'no-store' })
                .then(r => r.json())
                .then(data => {
                    const newIds = data.messages.map(m => m.id).join(',');
                    const lastMsgText = data.messages.length > 0 ? data.messages[data.messages.length - 1].text : "";
                    const containerLastText = container.lastChild ? container.lastChild.innerText : "";

                    if ((newIds !== currentIds || lastMsgText !== containerLastText) && data.messages.length > 0) {
                        currentIds = newIds;
                        renderMessages(data.messages);
                        container.classList.remove('hidden');
                        clearTimeout(hideTimeout);
                        hideTimeout = setTimeout(() => {
                            container.classList.add('hidden');
                        }, 7000);
                    }
                })
                .catch(e => console.error(e));
        }, 300);
    </script>
</body>
</html>"""