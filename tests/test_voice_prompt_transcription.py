from spaosi_voice_translator.services.obs.obs_server import strip_voice_transcription
from spaosi_voice_translator.services.translation.prompts import build_prompt


def test_voice_prompt_builds_pronunciation_guide_for_translation_not_source():
    prompt = build_prompt(
        target_text="Hello, how are you?",
        is_voice_mode=True,
        target_lang="Русский",
        source_lang="English",
    )

    assert "ИСХОДНЫЙ ЯЗЫК: English" in prompt
    assert "ЯЗЫК ПЕРЕВОДА: Русский" in prompt
    assert "подсказку произношения именно ПЕРЕВОДА" in prompt
    assert "Скобки НЕ должны быть транскрипцией исходной фразы" in prompt
    assert "Здравствуйте, как дела? [zdravstvuyte, kak dela?]" in prompt


def test_voice_prompt_uses_source_language_alphabet_for_guide():
    prompt = build_prompt(
        target_text="Привет, как дела?",
        is_voice_mode=True,
        target_lang="English",
        source_lang="Russian",
    )

    assert "Hello, how are you? [хэллоу, хау ар ю?]" in prompt
    assert "буквами и фонетикой ИСХОДНОГО ЯЗЫКА" in prompt
    assert "как произнести этот перевод для носителя Russian" in prompt


def test_obs_strips_latin_pronunciation_guide_from_mic_text():
    text = "Здравствуйте, как дела? [zdravstvuyte, kak dela?]"

    assert strip_voice_transcription(text) == "Здравствуйте, как дела?"


def test_obs_strips_cyrillic_pronunciation_guide_from_mic_text():
    text = "Hello, how are you? [хэллоу, хау ар ю?]"

    assert strip_voice_transcription(text) == "Hello, how are you?"
