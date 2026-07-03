from spaosi_voice_translator.core.i18n import Translator, UI_LANGUAGES, _TRANSLATIONS
from spaosi_voice_translator.core.settings import SettingsStore


def test_translator_defaults_to_russian(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.local.json")
    store.load()

    translator = Translator(store)
    translator.reload_from_settings()

    assert translator.language_code() == "ru"
    assert translator.t("main.start") == "ПУСК"


def test_translator_persists_english(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.local.json")
    translator = Translator(store)

    translator.set_language("en")
    store.save()

    loaded = SettingsStore(path=store.path)
    loaded.load()
    reloaded = Translator(loaded)
    reloaded.reload_from_settings()

    assert reloaded.language_code() == "en"
    assert reloaded.is_language_selected()
    assert reloaded.t("main.start") == "START"


def test_translator_persists_spanish_french_and_german(tmp_path):
    expected = {
        "es": "INICIAR",
        "fr": "DÉMARRER",
        "de": "START",
    }

    for language_code, start_text in expected.items():
        store = SettingsStore(path=tmp_path / f"{language_code}.json")
        translator = Translator(store)

        translator.set_language(language_code)

        assert translator.language_code() == language_code
        assert translator.t("main.start") == start_text


def test_all_declared_ui_languages_are_enabled_and_translated(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.local.json")
    translator = Translator(store)

    language_codes = {language.code for language in UI_LANGUAGES}
    assert language_codes == {"ru", "en", "es", "fr", "de"}
    assert all(language.enabled for language in UI_LANGUAGES)

    reference_keys = set(_TRANSLATIONS["en"].keys())
    for language in UI_LANGUAGES:
        translator.set_language(language.code)
        assert set(_TRANSLATIONS[language.code].keys()) == reference_keys
        assert translator.t("settings.title") != "settings.title"


def test_translator_uses_key_fallback_for_missing_string(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.local.json")
    translator = Translator(store)

    assert translator.t("missing.key") == "missing.key"


def test_deepgram_engine_removes_broken_ssl_paths(monkeypatch, tmp_path):
    import os
    import sys
    import types

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

    from spaosi_voice_translator.services.speech.deepgram_engine import DeepgramEngine

    missing = tmp_path / "missing-ca.pem"
    monkeypatch.setenv("SSL_CERT_FILE", str(missing))
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", str(missing))
    monkeypatch.setenv("CURL_CA_BUNDLE", str(missing))

    engine = DeepgramEngine("test", name="TEST")
    engine._prepare_tls_environment()

    assert "CURL_CA_BUNDLE" not in os.environ
    assert os.environ.get("SSL_CERT_FILE", "") != str(missing)
    assert os.environ.get("REQUESTS_CA_BUNDLE", "") != str(missing)

def test_microphone_overlay_hotkey_hint_is_translated(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.local.json")
    translator = Translator(store)

    translator.set_language("ru")
    assert translator.t("voice.press_hotkey_again") == "Нажми горячую кнопку ещё раз, чтобы перевести"

    translator.set_language("en")
    assert translator.t("voice.press_hotkey_again") == "Press the hotkey again to translate"

def test_obs_size_hint_is_translated(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.local.json")
    translator = Translator(store)

    translator.set_language("ru")
    assert translator.t("settings.obs_size_hint") == "Размер источника OBS: 1920×1080"

    translator.set_language("en")
    assert translator.t("settings.obs_size_hint") == "OBS source size: 1920×1080"

def test_gemini_proxy_settings_are_translated(tmp_path):
    store = SettingsStore(path=tmp_path / "settings.local.json")
    translator = Translator(store)

    translator.set_language("ru")
    assert translator.t("settings.row.gemini_proxy") == "Gemini proxy"
    assert translator.t("settings.gemini_proxy_placeholder") == "Optional Gemini proxy URL"
    assert "напрямую" in translator.t("settings.gemini_proxy_tooltip")

    translator.set_language("en")
    assert translator.t("settings.gemini_proxy_tooltip").startswith("Optional Gemini proxy")
