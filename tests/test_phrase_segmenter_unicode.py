from spaosi_voice_translator.services.pipeline.phrase_segmenter import (
    RealtimePhraseSegmenter,
)


def test_final_japanese_phrase_is_not_dropped() -> None:
    segmenter = RealtimePhraseSegmenter()

    result = segmenter.push(
        "嫌いな国とかってどこかあったりします？",
        is_final=True,
        speech_final=True,
    )

    assert result == ["嫌いな国とかってどこかあったりします？"]


def test_final_japanese_phrase_deduplicates_normally() -> None:
    segmenter = RealtimePhraseSegmenter()
    phrase = "今日は日本について話します。"

    first = segmenter.push(phrase, is_final=True, speech_final=True)
    second = segmenter.push(phrase, is_final=True, speech_final=True)

    assert first == [phrase]
    assert second == []


def test_final_chinese_phrase_is_not_dropped() -> None:
    segmenter = RealtimePhraseSegmenter()

    result = segmenter.push(
        "你今天想去哪里？",
        is_final=True,
        speech_final=True,
    )

    assert result == ["你今天想去哪里？"]


def test_existing_english_behavior_still_works() -> None:
    segmenter = RealtimePhraseSegmenter()

    result = segmenter.push(
        "This is a normal English sentence.",
        is_final=True,
        speech_final=True,
    )

    assert result == ["This is a normal English sentence."]
