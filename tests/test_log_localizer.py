from spaosi_voice_translator.core.log_localizer import localize_log_line


def test_log_localizer_translates_russian_service_logs_to_english():
    assert (
        localize_log_line(
            "18:26:03: SYS запущен: режим Realtime. Язык=en, цель=Русский, пауза=600 мс, лимит фразы=14 слов",
            "en",
        )
        == "18:26:03: SYS started: Realtime mode. Language=en, target=Русский, pause=600 ms, phrase limit=14 words"
    )
    assert (
        localize_log_line("Deepgram[EXTERNAL]: канал остановлен", "en")
        == "Deepgram[EXTERNAL]: channel stopped"
    )
    assert (
        localize_log_line("Gemini[EXTERNAL]: остановлен", "en")
        == "Gemini[EXTERNAL]: stopped"
    )
    assert (
        localize_log_line("Канал Deepgram для внешних голосов готов", "en")
        == "Deepgram channel for external voices is ready"
    )


def test_log_localizer_translates_english_service_logs_to_russian():
    assert (
        localize_log_line("SYS is not running: system audio is not being captured", "ru")
        == "SYS не запущен: звук системы не слушается"
    )
    assert (
        localize_log_line("Deepgram[EXTERNAL]: connected in 1167 ms", "ru")
        == "Deepgram[EXTERNAL]: подключение установлено за 1167 мс"
    )


def test_log_localizer_keeps_gemini_http_details():
    assert (
        localize_log_line("Ошибка Gemini[EXTERNAL]: HTTP 400: INVALID_ARGUMENT: bad request", "en")
        == "Gemini[EXTERNAL] error: HTTP 400: INVALID_ARGUMENT: bad request"
    )
