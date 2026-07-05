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

    assert url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
    assert headers["x-goog-api-key"] == "test-key"
    assert "key=" not in url

    translator.stop()


def test_gemini_proxy_keeps_query_key_for_compatibility(monkeypatch):
    _install_fake_pyqt(monkeypatch)

    from spaosi_voice_translator.services.translation.gemini_translator import GeminiTranslator

    translator = GeminiTranslator("test-key", proxy_url="http://127.0.0.1:8080")
    url, headers = translator._build_request_url_and_headers()

    assert url == "http://127.0.0.1:8080/v1beta/models/gemini-3.1-flash-lite:generateContent?key=test-key"
    assert "x-goog-api-key" not in headers

    translator.stop()
