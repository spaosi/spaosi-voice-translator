from __future__ import annotations

import re
from typing import Match


_TIMESTAMP_RE = re.compile(r"^(?P<prefix>\d{2}:\d{2}:\d{2}:\s*)(?P<body>.*)$")

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "settings_loaded": "Настройки загружены",
        "interface_loaded": "Интерфейс загружен",
        "windows_created": "Окна интерфейса созданы",
        "app_ready": "Приложение готово",
        "obs_started": "OBS виджет запущен: {url}",
        "obs_error": "Ошибка OBS виджета: {error}",
        "hotkey_registered": "MIC хоткей зарегистрирован: {hotkey}",
        "hotkey_selected": "MIC хоткей выбран: {hotkey}",
        "hotkey_empty": "Хоткей микрофона пустой",
        "hotkey_missing_dependency": "Ошибка хоткея: не хватает зависимости keyboard. Установи зависимости через pip install -e .",
        "hotkey_register_failed": "Ошибка хоткея: не удалось зарегистрировать {hotkey}: {error}",

        "sys_started_realtime": "SYS запущен: режим Realtime. Язык={language}, цель={target}, пауза={pause} мс, лимит фразы=14 слов",
        "sys_started_video": "SYS запущен: режим Видео перевода. Язык={language}, цель={target}, пауза=600 мс, лимит фразы=без ограничений, OBS=без обрезки",
        "sys_idle": "SYS не запущен: звук системы не слушается",
        "sys_deepgram_key_empty": "Ошибка: ключ Deepgram пустой",
        "sys_gemini_key_empty": "Ошибка: ключ Gemini пустой, перевод отключён",
        "early_translation": "Ранний перевод: фраза разбита до финального пакета Deepgram, частей={parts}",
        "external_incoming": "Внешние голоса: {text}",
        "translation": "Перевод: {text}",
        "mic_translation": "Перевод микрофона: {text}",

        "deepgram_connecting": "Deepgram[{name}]: подключение, язык={language}, пауза={pause} мс",
        "deepgram_connected": "Deepgram[{name}]: подключение установлено за {ms} мс",
        "deepgram_stopped": "Deepgram[{name}]: канал остановлен",
        "deepgram_external_ready": "Канал Deepgram для внешних голосов готов",
        "deepgram_mic_ready": "Канал Deepgram для микрофона готов",
        "deepgram_missing_sdk": "Ошибка Deepgram: не хватает deepgram-sdk. Установи зависимости через pip install -e .",
        "deepgram_cert": "Ошибка Deepgram: WebSocket не смог найти SSL/cert файл. Проверь обновление зависимостей через pip install -e .",
        "deepgram_connect_failed": "Ошибка Deepgram[{name}]: не удалось подключиться: {error}",
        "deepgram_closed": "Ошибка Deepgram[{name}]: соединение закрыто, переподключение",
        "deepgram_reconnect_stopped": "Ошибка Deepgram[{name}]: переподключение остановлено после {attempts} попыток",
        "deepgram_lost": "Deepgram[{name}]: WebSocket потерян ({reason}), попытка {attempt}/{max_attempts} через {delay} сек",
        "deepgram_keepalive_failed": "Ошибка Deepgram: keepalive не прошел: {error}",
        "deepgram_send_failed": "Ошибка Deepgram: отправка аудио не удалась: {error}",
        "deepgram_generic": "Ошибка Deepgram: {error}",
        "deepgram_file_error": "Deepgram[{name}]: {error}",

        "gemini_queue_added": "Gemini[{name}]: фраза добавлена в очередь, длина={length}",
        "gemini_queue_full": "Ошибка Gemini[{name}]: очередь перевода заполнена, фраза пропущена",
        "gemini_drained": "Gemini[{name}]: очищено ожидающих переводов: {count}",
        "gemini_stopped": "Gemini[{name}]: остановлен",
        "gemini_queue_took": "Gemini[{name}]: взял фразу из очереди за {ms} мс",
        "gemini_empty_key": "Ошибка Gemini: ключ Gemini пустой, перевод отключён",
        "gemini_auto_filter": "Gemini[{name}]: авто-фильтр, русский текст пропущен",
        "gemini_request_failed": "Ошибка Gemini[{name}]: запрос не удался: {error}",
        "gemini_http": "Ошибка Gemini[{name}]: HTTP {status}{details}",
        "gemini_parse": "Ошибка Gemini[{name}]: не удалось прочитать ответ: {error}",
        "gemini_empty_response": "Gemini[{name}]: пустой ответ модели",
        "gemini_wait": "Gemini[{name}]: WAIT, фрагмент пропущен",
        "gemini_repeat": "Gemini[{name}]: повтор перевода пропущен",
        "gemini_ready": "Gemini[{name}]: перевод готов за {ms} мс{trace}",

        "mic_deepgram_key_empty": "Ошибка MIC: ключ Deepgram пустой",
        "mic_gemini_key_empty": "Ошибка MIC: ключ Gemini пустой",
        "mic_restart": "MIC: настройки распознавания изменились, перезапуск канала Deepgram на языке={language}",
        "mic_starting": "MIC сервис запускается: Deepgram={language}, пауза={pause} мс, исходный язык={source}, цель={target}",
        "mic_recording_started": "MIC: запись включена. Говори фразу, потом нажми хоткей ещё раз",
        "mic_recording_empty": "MIC: запись остановлена, текста нет",
        "mic_incoming": "Микрофон: {text}",
        "mic_phrase_sent": "MIC: фраза отправлена в Gemini, len={length}",

        "audio_missing_dependency": "Ошибка Windows Audio API: не хватает зависимости. Установи зависимости через pip install -e .",
        "audio_system_capture": "Захват системного звука: {device}",
        "audio_mic_capture": "Захват микрофона: {device}",
        "audio_system_lost": "Ошибка Windows Audio API: захват звука потерян: {error}",
        "audio_mic_lost": "Ошибка Windows Audio API: захват микрофона потерян: {error}",
        "audio_system_not_found": "Ошибка Windows Audio API: выбранное устройство не найдено, используется стандартное",
        "audio_mic_not_found": "Ошибка Windows Audio API: выбранный микрофон не найден, используется стандартный",

        "obs_external": "OBS: показан текст ({mode}): {text}",
        "obs_mic": "OBS: показан MIC текст: {text}",
        "obs_mode_no_trim": "без обрезки",
        "obs_mode_regular": "обычный",
    },
    "en": {
        "settings_loaded": "Settings loaded",
        "interface_loaded": "Interface loaded",
        "windows_created": "Interface windows created",
        "app_ready": "Application ready",
        "obs_started": "OBS widget started: {url}",
        "obs_error": "OBS widget error: {error}",
        "hotkey_registered": "MIC hotkey registered: {hotkey}",
        "hotkey_selected": "MIC hotkey selected: {hotkey}",
        "hotkey_empty": "Microphone hotkey is empty",
        "hotkey_missing_dependency": "Hotkey error: missing keyboard dependency. Install dependencies with pip install -e .",
        "hotkey_register_failed": "Hotkey error: failed to register {hotkey}: {error}",

        "sys_started_realtime": "SYS started: Realtime mode. Language={language}, target={target}, pause={pause} ms, phrase limit=14 words",
        "sys_started_video": "SYS started: Video translation mode. Language={language}, target={target}, pause=600 ms, phrase limit=none, OBS=no trimming",
        "sys_idle": "SYS is not running: system audio is not being captured",
        "sys_deepgram_key_empty": "Error: Deepgram key is empty",
        "sys_gemini_key_empty": "Error: Gemini key is empty, translation disabled",
        "early_translation": "Early translation: phrase split before final Deepgram packet, parts={parts}",
        "external_incoming": "External voices: {text}",
        "translation": "Translation: {text}",
        "mic_translation": "Microphone translation: {text}",

        "deepgram_connecting": "Deepgram[{name}]: connecting, language={language}, pause={pause} ms",
        "deepgram_connected": "Deepgram[{name}]: connected in {ms} ms",
        "deepgram_stopped": "Deepgram[{name}]: channel stopped",
        "deepgram_external_ready": "Deepgram channel for external voices is ready",
        "deepgram_mic_ready": "Deepgram channel for microphone is ready",
        "deepgram_missing_sdk": "Deepgram error: deepgram-sdk is missing. Install dependencies with pip install -e .",
        "deepgram_cert": "Deepgram error: WebSocket could not find the SSL/cert file. Update dependencies with pip install -e .",
        "deepgram_connect_failed": "Deepgram[{name}] error: failed to connect: {error}",
        "deepgram_closed": "Deepgram[{name}] error: connection closed, reconnecting",
        "deepgram_reconnect_stopped": "Deepgram[{name}] error: reconnect stopped after {attempts} attempts",
        "deepgram_lost": "Deepgram[{name}]: WebSocket lost ({reason}), attempt {attempt}/{max_attempts} in {delay} sec",
        "deepgram_keepalive_failed": "Deepgram error: keepalive failed: {error}",
        "deepgram_send_failed": "Deepgram error: failed to send audio: {error}",
        "deepgram_generic": "Deepgram error: {error}",
        "deepgram_file_error": "Deepgram[{name}]: {error}",

        "gemini_queue_added": "Gemini[{name}]: phrase added to queue, length={length}",
        "gemini_queue_full": "Gemini[{name}] error: translation queue is full, phrase skipped",
        "gemini_drained": "Gemini[{name}]: cleared pending translations: {count}",
        "gemini_stopped": "Gemini[{name}]: stopped",
        "gemini_queue_took": "Gemini[{name}]: took phrase from queue after {ms} ms",
        "gemini_empty_key": "Gemini error: Gemini key is empty, translation disabled",
        "gemini_auto_filter": "Gemini[{name}]: auto-filter, Russian text skipped",
        "gemini_request_failed": "Gemini[{name}] error: request failed: {error}",
        "gemini_http": "Gemini[{name}] error: HTTP {status}{details}",
        "gemini_parse": "Gemini[{name}] error: failed to read response: {error}",
        "gemini_empty_response": "Gemini[{name}]: empty model response",
        "gemini_wait": "Gemini[{name}]: WAIT, fragment skipped",
        "gemini_repeat": "Gemini[{name}]: repeated translation skipped",
        "gemini_ready": "Gemini[{name}]: translation ready in {ms} ms{trace}",

        "mic_deepgram_key_empty": "MIC error: Deepgram key is empty",
        "mic_gemini_key_empty": "MIC error: Gemini key is empty",
        "mic_restart": "MIC: recognition settings changed, restarting Deepgram channel with language={language}",
        "mic_starting": "MIC service starting: Deepgram={language}, pause={pause} ms, source language={source}, target={target}",
        "mic_recording_started": "MIC: recording enabled. Say a phrase, then press the hotkey again",
        "mic_recording_empty": "MIC: recording stopped, no text",
        "mic_incoming": "Microphone: {text}",
        "mic_phrase_sent": "MIC: phrase sent to Gemini, len={length}",

        "audio_missing_dependency": "Windows Audio API error: missing dependency. Install dependencies with pip install -e .",
        "audio_system_capture": "System audio capture: {device}",
        "audio_mic_capture": "Microphone capture: {device}",
        "audio_system_lost": "Windows Audio API error: audio capture lost: {error}",
        "audio_mic_lost": "Windows Audio API error: microphone capture lost: {error}",
        "audio_system_not_found": "Windows Audio API error: selected device not found, using default",
        "audio_mic_not_found": "Windows Audio API error: selected microphone not found, using default",

        "obs_external": "OBS: shown text ({mode}): {text}",
        "obs_mic": "OBS: shown MIC text: {text}",
        "obs_mode_no_trim": "no trimming",
        "obs_mode_regular": "regular",
    },
}

# For now service logs are normalized to Russian or English. Other UI languages keep
# English service logs instead of leaking mixed Russian/English technical strings.
_FALLBACK_LANGUAGE = "en"

_RULES: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern), key)
    for pattern, key in (
        (r"^Настройки загружены$", "settings_loaded"),
        (r"^Settings loaded$", "settings_loaded"),
        (r"^Интерфейс загружен$", "interface_loaded"),
        (r"^Interface loaded$", "interface_loaded"),
        (r"^Окна интерфейса созданы$", "windows_created"),
        (r"^Interface windows created$", "windows_created"),
        (r"^Приложение готово$", "app_ready"),
        (r"^Application ready$", "app_ready"),
        (r"^OBS виджет запущен: (?P<url>.+)$", "obs_started"),
        (r"^OBS widget started: (?P<url>.+)$", "obs_started"),
        (r"^Ошибка OBS виджета: (?P<error>.+)$", "obs_error"),
        (r"^OBS widget error: (?P<error>.+)$", "obs_error"),
        (r"^MIC хоткей зарегистрирован: (?P<hotkey>.+)$", "hotkey_registered"),
        (r"^MIC hotkey registered: (?P<hotkey>.+)$", "hotkey_registered"),
        (r"^MIC хоткей выбран: (?P<hotkey>.+)$", "hotkey_selected"),
        (r"^MIC hotkey selected: (?P<hotkey>.+)$", "hotkey_selected"),
        (r"^Хоткей микрофона пустой$", "hotkey_empty"),
        (r"^Microphone hotkey is empty$", "hotkey_empty"),
        (r"^Ошибка хоткея: не хватает зависимости keyboard\. Установи зависимости через pip install -e \.$", "hotkey_missing_dependency"),
        (r"^Hotkey error: missing keyboard dependency\. Install dependencies with pip install -e \.$", "hotkey_missing_dependency"),
        (r"^Ошибка хоткея: не удалось зарегистрировать (?P<hotkey>.+?): (?P<error>.+)$", "hotkey_register_failed"),
        (r"^Hotkey error: failed to register (?P<hotkey>.+?): (?P<error>.+)$", "hotkey_register_failed"),

        (r"^SYS запущен: режим Realtime\. Язык=(?P<language>[^,]+), цель=(?P<target>[^,]+), пауза=(?P<pause>\d+) мс, лимит фразы=14 слов$", "sys_started_realtime"),
        (r"^SYS started: Realtime mode\. Language=(?P<language>[^,]+), target=(?P<target>[^,]+), pause=(?P<pause>\d+) ms, phrase limit=14 words$", "sys_started_realtime"),
        (r"^SYS запущен: режим Видео перевода\. Язык=(?P<language>[^,]+), цель=(?P<target>[^,]+), пауза=600 мс, лимит фразы=без ограничений, OBS=без обрезки$", "sys_started_video"),
        (r"^SYS started: Video translation mode\. Language=(?P<language>[^,]+), target=(?P<target>[^,]+), pause=600 ms, phrase limit=none, OBS=no trimming$", "sys_started_video"),
        (r"^SYS не запущен: звук системы не слушается$", "sys_idle"),
        (r"^SYS is not running: system audio is not being captured$", "sys_idle"),
        (r"^Ошибка: ключ Deepgram пустой$", "sys_deepgram_key_empty"),
        (r"^Error: Deepgram key is empty$", "sys_deepgram_key_empty"),
        (r"^Ошибка: ключ Gemini пустой, перевод отключён$", "sys_gemini_key_empty"),
        (r"^Error: Gemini key is empty, translation disabled$", "sys_gemini_key_empty"),
        (r"^Ранний перевод: фраза разбита до финального пакета Deepgram, частей=(?P<parts>\d+)$", "early_translation"),
        (r"^Early translation: phrase split before final Deepgram packet, parts=(?P<parts>\d+)$", "early_translation"),
        (r"^Внешние голоса: (?P<text>.+)$", "external_incoming"),
        (r"^External voices: (?P<text>.+)$", "external_incoming"),
        (r"^Перевод: (?P<text>.+)$", "translation"),
        (r"^Translation: (?P<text>.+)$", "translation"),
        (r"^Перевод микрофона: (?P<text>.+)$", "mic_translation"),
        (r"^Microphone translation: (?P<text>.+)$", "mic_translation"),

        (r"^Deepgram\[(?P<name>[^\]]+)\]: подключение, язык=(?P<language>[^,]+), пауза=(?P<pause>\d+) мс$", "deepgram_connecting"),
        (r"^Deepgram\[(?P<name>[^\]]+)\]: connecting, language=(?P<language>[^,]+), pause=(?P<pause>\d+) ms$", "deepgram_connecting"),
        (r"^Deepgram\[(?P<name>[^\]]+)\]: подключение установлено за (?P<ms>\d+) мс$", "deepgram_connected"),
        (r"^Deepgram\[(?P<name>[^\]]+)\]: connected in (?P<ms>\d+) ms$", "deepgram_connected"),
        (r"^Deepgram\[(?P<name>[^\]]+)\]: канал остановлен$", "deepgram_stopped"),
        (r"^Deepgram\[(?P<name>[^\]]+)\]: channel stopped$", "deepgram_stopped"),
        (r"^Канал Deepgram для внешних голосов готов$", "deepgram_external_ready"),
        (r"^Deepgram channel for external voices is ready$", "deepgram_external_ready"),
        (r"^Канал Deepgram для микрофона готов$", "deepgram_mic_ready"),
        (r"^Deepgram channel for microphone is ready$", "deepgram_mic_ready"),
        (r"^Ошибка Deepgram: не хватает deepgram-sdk\. Установи зависимости через pip install -e \.$", "deepgram_missing_sdk"),
        (r"^Deepgram error: deepgram-sdk is missing\. Install dependencies with pip install -e \.$", "deepgram_missing_sdk"),
        (r"^Ошибка Deepgram: WebSocket не смог найти SSL/cert файл\. Проверь обновление зависимостей через pip install -e \.$", "deepgram_cert"),
        (r"^Deepgram error: WebSocket could not find the SSL/cert file\. Update dependencies with pip install -e \.$", "deepgram_cert"),
        (r"^Ошибка Deepgram\[(?P<name>[^\]]+)\]: не удалось подключиться: (?P<error>.+)$", "deepgram_connect_failed"),
        (r"^Deepgram\[(?P<name>[^\]]+)\] error: failed to connect: (?P<error>.+)$", "deepgram_connect_failed"),
        (r"^Ошибка Deepgram\[(?P<name>[^\]]+)\]: соединение закрыто, переподключение$", "deepgram_closed"),
        (r"^Deepgram\[(?P<name>[^\]]+)\] error: connection closed, reconnecting$", "deepgram_closed"),
        (r"^Ошибка Deepgram\[(?P<name>[^\]]+)\]: переподключение остановлено после (?P<attempts>\d+) попыток$", "deepgram_reconnect_stopped"),
        (r"^Deepgram\[(?P<name>[^\]]+)\] error: reconnect stopped after (?P<attempts>\d+) attempts$", "deepgram_reconnect_stopped"),
        (r"^Deepgram\[(?P<name>[^\]]+)\]: WebSocket потерян \((?P<reason>.+)\), попытка (?P<attempt>\d+)/(?P<max_attempts>\d+) через (?P<delay>[\d.]+) сек$", "deepgram_lost"),
        (r"^Deepgram\[(?P<name>[^\]]+)\]: WebSocket lost \((?P<reason>.+)\), attempt (?P<attempt>\d+)/(?P<max_attempts>\d+) in (?P<delay>[\d.]+) sec$", "deepgram_lost"),
        (r"^Ошибка Deepgram: keepalive не прошел: (?P<error>.+)$", "deepgram_keepalive_failed"),
        (r"^Deepgram error: keepalive failed: (?P<error>.+)$", "deepgram_keepalive_failed"),
        (r"^Ошибка Deepgram: отправка аудио не удалась: (?P<error>.+)$", "deepgram_send_failed"),
        (r"^Deepgram error: failed to send audio: (?P<error>.+)$", "deepgram_send_failed"),
        (r"^Ошибка Deepgram: (?P<error>.+)$", "deepgram_generic"),
        (r"^Deepgram error: (?P<error>.+)$", "deepgram_generic"),

        (r"^Gemini\[(?P<name>[^\]]+)\]: фраза добавлена в очередь, длина=(?P<length>\d+)$", "gemini_queue_added"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: phrase added to queue, length=(?P<length>\d+)$", "gemini_queue_added"),
        (r"^Ошибка Gemini\[(?P<name>[^\]]+)\]: очередь перевода заполнена, фраза пропущена$", "gemini_queue_full"),
        (r"^Gemini\[(?P<name>[^\]]+)\] error: translation queue is full, phrase skipped$", "gemini_queue_full"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: очищено ожидающих переводов: (?P<count>\d+)$", "gemini_drained"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: cleared pending translations: (?P<count>\d+)$", "gemini_drained"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: остановлен$", "gemini_stopped"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: stopped$", "gemini_stopped"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: взял фразу из очереди за (?P<ms>\d+) мс$", "gemini_queue_took"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: took phrase from queue after (?P<ms>\d+) ms$", "gemini_queue_took"),
        (r"^Ошибка Gemini: ключ Gemini пустой, перевод отключён$", "gemini_empty_key"),
        (r"^Gemini error: Gemini key is empty, translation disabled$", "gemini_empty_key"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: авто-фильтр, русский текст пропущен$", "gemini_auto_filter"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: auto-filter, Russian text skipped$", "gemini_auto_filter"),
        (r"^Ошибка Gemini\[(?P<name>[^\]]+)\]: запрос не удался: (?P<error>.+)$", "gemini_request_failed"),
        (r"^Gemini\[(?P<name>[^\]]+)\] error: request failed: (?P<error>.+)$", "gemini_request_failed"),
        (r"^Ошибка Gemini\[(?P<name>[^\]]+)\]: HTTP (?P<status>\d+)(?P<details>: .*)?$", "gemini_http"),
        (r"^Gemini\[(?P<name>[^\]]+)\] error: HTTP (?P<status>\d+)(?P<details>: .*)?$", "gemini_http"),
        (r"^Ошибка Gemini\[(?P<name>[^\]]+)\]: не удалось прочитать ответ: (?P<error>.+)$", "gemini_parse"),
        (r"^Gemini\[(?P<name>[^\]]+)\] error: failed to read response: (?P<error>.+)$", "gemini_parse"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: пустой ответ модели$", "gemini_empty_response"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: empty model response$", "gemini_empty_response"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: WAIT, фрагмент пропущен$", "gemini_wait"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: WAIT, fragment skipped$", "gemini_wait"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: повтор перевода пропущен$", "gemini_repeat"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: repeated translation skipped$", "gemini_repeat"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: перевод готов за (?P<ms>\d+) мс(?P<trace>.*)$", "gemini_ready"),
        (r"^Gemini\[(?P<name>[^\]]+)\]: translation ready in (?P<ms>\d+) ms(?P<trace>.*)$", "gemini_ready"),

        (r"^Ошибка MIC: ключ Deepgram пустой$", "mic_deepgram_key_empty"),
        (r"^MIC error: Deepgram key is empty$", "mic_deepgram_key_empty"),
        (r"^Ошибка MIC: ключ Gemini пустой$", "mic_gemini_key_empty"),
        (r"^MIC error: Gemini key is empty$", "mic_gemini_key_empty"),
        (r"^MIC: настройки распознавания изменились, перезапуск канала Deepgram на языке=(?P<language>.+)$", "mic_restart"),
        (r"^MIC: recognition settings changed, restarting Deepgram channel with language=(?P<language>.+)$", "mic_restart"),
        (r"^MIC сервис запускается: Deepgram=(?P<language>[^,]+), пауза=(?P<pause>\d+) мс, исходный язык=(?P<source>[^,]+), цель=(?P<target>.+)$", "mic_starting"),
        (r"^MIC service starting: Deepgram=(?P<language>[^,]+), pause=(?P<pause>\d+) ms, source language=(?P<source>[^,]+), target=(?P<target>.+)$", "mic_starting"),
        (r"^MIC: запись включена\. Говори фразу, потом нажми хоткей ещё раз$", "mic_recording_started"),
        (r"^MIC: recording enabled\. Say a phrase, then press the hotkey again$", "mic_recording_started"),
        (r"^MIC: запись остановлена, текста нет$", "mic_recording_empty"),
        (r"^MIC: recording stopped, no text$", "mic_recording_empty"),
        (r"^Микрофон: (?P<text>.+)$", "mic_incoming"),
        (r"^Microphone: (?P<text>.+)$", "mic_incoming"),
        (r"^MIC: фраза отправлена в Gemini, len=(?P<length>\d+)$", "mic_phrase_sent"),
        (r"^MIC: phrase sent to Gemini, len=(?P<length>\d+)$", "mic_phrase_sent"),

        (r"^Ошибка Windows Audio API: не хватает зависимости\. Установи зависимости через pip install -e \.$", "audio_missing_dependency"),
        (r"^Windows Audio API error: missing dependency\. Install dependencies with pip install -e \.$", "audio_missing_dependency"),
        (r"^Захват системного звука: (?P<device>.+)$", "audio_system_capture"),
        (r"^System audio capture: (?P<device>.+)$", "audio_system_capture"),
        (r"^Захват микрофона: (?P<device>.+)$", "audio_mic_capture"),
        (r"^Microphone capture: (?P<device>.+)$", "audio_mic_capture"),
        (r"^Ошибка Windows Audio API: захват звука потерян: (?P<error>.+)$", "audio_system_lost"),
        (r"^Windows Audio API error: audio capture lost: (?P<error>.+)$", "audio_system_lost"),
        (r"^Ошибка Windows Audio API: захват микрофона потерян: (?P<error>.+)$", "audio_mic_lost"),
        (r"^Windows Audio API error: microphone capture lost: (?P<error>.+)$", "audio_mic_lost"),
        (r"^Ошибка Windows Audio API: выбранное устройство не найдено, используется стандартное$", "audio_system_not_found"),
        (r"^Windows Audio API error: selected device not found, using default$", "audio_system_not_found"),
        (r"^Ошибка Windows Audio API: выбранный микрофон не найден, используется стандартный$", "audio_mic_not_found"),
        (r"^Windows Audio API error: selected microphone not found, using default$", "audio_mic_not_found"),

        (r"^OBS: показан текст \((?P<mode>без обрезки|обычный|no trimming|regular)\): (?P<text>.*)$", "obs_external"),
        (r"^OBS: shown text \((?P<mode>no trimming|regular|без обрезки|обычный)\): (?P<text>.*)$", "obs_external"),
        (r"^OBS: показан MIC текст: (?P<text>.*)$", "obs_mic"),
        (r"^OBS: shown MIC text: (?P<text>.*)$", "obs_mic"),
    )
)


def localize_log_line(line: str, language_code: str) -> str:
    raw = str(line or "")
    timestamp = _TIMESTAMP_RE.match(raw)
    if timestamp:
        return timestamp.group("prefix") + localize_log_body(timestamp.group("body"), language_code)

    return localize_log_body(raw, language_code)


def localize_log_body(body: str, language_code: str) -> str:
    clean = str(body or "").strip()
    if not clean:
        return clean

    lang = _select_language(language_code)

    for pattern, key in _RULES:
        match = pattern.match(clean)
        if not match:
            continue
        return _format(lang, key, match)

    return clean


def _select_language(language_code: str) -> str:
    clean = str(language_code or "").strip().lower()
    if clean in _TRANSLATIONS:
        return clean
    return _FALLBACK_LANGUAGE


def _format(language_code: str, key: str, match: Match[str]) -> str:
    values = {name: value or "" for name, value in match.groupdict().items()}

    if key == "obs_external":
        mode = values.get("mode", "")
        if mode in {"без обрезки", "no trimming"}:
            values["mode"] = _TRANSLATIONS[language_code]["obs_mode_no_trim"]
        elif mode in {"обычный", "regular"}:
            values["mode"] = _TRANSLATIONS[language_code]["obs_mode_regular"]

    if key == "gemini_http":
        details = values.get("details", "")
        if details:
            values["details"] = _trim_details(details)
        else:
            values["details"] = ""

    template = _TRANSLATIONS[language_code].get(key) or _TRANSLATIONS[_FALLBACK_LANGUAGE].get(key)
    if not template:
        return match.group(0)

    try:
        return template.format(**values)
    except Exception:
        return match.group(0)


def _trim_details(details: str) -> str:
    clean = re.sub(r"\s+", " ", str(details or "").strip())
    if len(clean) > 260:
        clean = clean[:257].rstrip() + "..."
    return clean
