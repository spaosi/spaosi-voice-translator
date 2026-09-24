import sys
import types


def _install_fake_pyqt(monkeypatch):
    qtcore = types.ModuleType("PyQt6.QtCore")

    class _FakeQObject:
        pass

    class _FakeSignal:
        def emit(self, *_args, **_kwargs):
            pass

    qtcore.QObject = _FakeQObject
    qtcore.pyqtSignal = lambda *args, **kwargs: _FakeSignal()

    pyqt6 = types.ModuleType("PyQt6")
    monkeypatch.setitem(sys.modules, "PyQt6", pyqt6)
    monkeypatch.setitem(sys.modules, "PyQt6.QtCore", qtcore)


def test_gemini_translator_normalizes_proxy_url(monkeypatch):
    _install_fake_pyqt(monkeypatch)

    from spaosi_voice_translator.services.translation.gemini_translator import GeminiTranslator

    translator = GeminiTranslator("test")

    assert translator.proxy_url == ""
    assert translator._api_base_url() == "https://generativelanguage.googleapis.com"

    translator.set_proxy_url("127.0.0.1:8080/")
    assert translator.proxy_url == "http://127.0.0.1:8080"
    assert translator._api_base_url() == "http://127.0.0.1:8080"

    translator.set_proxy_url("https://example.com/proxy/")
    assert translator.proxy_url == "https://example.com/proxy"

    translator.stop()


def test_gemini_direct_api_uses_header_key(monkeypatch):
    _install_fake_pyqt(monkeypatch)

    from spaosi_voice_translator.services.translation.gemini_translator import GeminiTranslator

    translator = GeminiTranslator("test-key")
    url, headers = translator._build_request_url_and_headers()

    assert url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
    assert headers["x-goog-api-key"] == "test-key"
    assert "key=" not in url

    translator.stop()


def test_gemini_proxy_keeps_query_key_for_compatibility(monkeypatch):
    _install_fake_pyqt(monkeypatch)

    from spaosi_voice_translator.services.translation.gemini_translator import GeminiTranslator

    translator = GeminiTranslator("test-key", proxy_url="http://127.0.0.1:8080")
    url, headers = translator._build_request_url_and_headers()

    assert url == "http://127.0.0.1:8080/v1beta/models/gemini-3.5-flash-lite:generateContent?key=test-key"
    assert "x-goog-api-key" not in headers

    translator.stop()


class _FakeResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self._text = text

    def json(self):
        if self.status_code == 200:
            return {"candidates": [{"content": {"parts": [{"text": self._text}]}}]}
        return {"error": {"status": "UNAVAILABLE", "message": "Test overload"}}


class _FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.models = []

    def post(self, url, **_kwargs):
        self.models.append(url.split("/models/")[1].split(":generateContent")[0])
        return next(self.responses)


def _translator_with_fake_responses(monkeypatch, responses):
    _install_fake_pyqt(monkeypatch)
    from spaosi_voice_translator.services.translation.gemini_translator import GeminiTranslator

    translator = GeminiTranslator("test-key")
    session = _FakeSession(responses)
    monkeypatch.setattr(translator, "_requests_session", lambda: session)
    emitted = []
    monkeypatch.setattr(translator.translation_ready, "emit", lambda *args: emitted.append(args))
    return translator, session, emitted


def test_gemini_503_falls_back_without_losing_phrase(monkeypatch):
    translator, session, emitted = _translator_with_fake_responses(
        monkeypatch, [_FakeResponse(503), _FakeResponse(200, "Привет")]
    )
    try:
        translator._translate_now(translator._generation, "Hello", "")
        assert session.models == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
        assert emitted == [("Hello", "Привет")]
        assert translator._fallback_until > 0
    finally:
        translator.stop()


def test_gemini_cooldown_uses_fallback_then_recovers(monkeypatch):
    translator, session, emitted = _translator_with_fake_responses(
        monkeypatch,
        [
            _FakeResponse(503),
            _FakeResponse(200, "Один"),
            _FakeResponse(200, "Два"),
            _FakeResponse(200, "Три"),
        ],
    )
    try:
        translator._translate_now(translator._generation, "One", "")
        translator._translate_now(translator._generation, "Two", "")
        translator._fallback_until = 0.0  # Simulate the end of the 60-second cooldown.
        translator._translate_now(translator._generation, "Three", "")
        assert session.models == [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash-lite",
        ]
        assert emitted == [("One", "Один"), ("Two", "Два"), ("Three", "Три")]
        assert translator._fallback_until == 0.0
    finally:
        translator.stop()


def test_gemini_does_not_fallback_for_non_503(monkeypatch):
    translator, session, emitted = _translator_with_fake_responses(
        monkeypatch, [_FakeResponse(400)]
    )
    try:
        translator._translate_now(translator._generation, "Hello", "")
        assert session.models == ["gemini-3.5-flash-lite"]
        assert emitted == []
    finally:
        translator.stop()


def test_gemini_handles_both_models_unavailable(monkeypatch):
    translator, session, emitted = _translator_with_fake_responses(
        monkeypatch, [_FakeResponse(503), _FakeResponse(503)]
    )
    try:
        translator._translate_now(translator._generation, "Hello", "")
        assert session.models == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
        assert emitted == []
    finally:
        translator.stop()
