from spaosi_voice_translator.core.settings import SettingsStore


def test_settings_store_roundtrip(tmp_path):
    path = tmp_path / "settings.local.json"
    store = SettingsStore(path=path)
    store.set("geometry.main_window", [1, 2, 3, 4])
    store.save()

    loaded = SettingsStore(path=path)
    loaded.load()

    assert loaded.get("geometry.main_window") == [1, 2, 3, 4]
