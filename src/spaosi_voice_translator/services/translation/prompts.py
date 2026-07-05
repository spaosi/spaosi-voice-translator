from __future__ import annotations


VOICE_PROMPT_TEMPLATE = (
    "Ты - профессиональный переводчик живой речи и специалист по произношению. "
    "Переведи ТОЛЬКО целевую фразу на {target_lang_upper} ЯЗЫК.\n"
    "ИСХОДНЫЙ ЯЗЫК: {source_lang}\n"
    "ЯЗЫК ПЕРЕВОДА: {target_lang}\n"
    "ЗАДАЧА:\n"
    "Дать перевод и подсказку произношения, чтобы человек, который знает ИСХОДНЫЙ ЯЗЫК, "
    "смог вслух произнести перевод на ЯЗЫКЕ ПЕРЕВОДА, даже если он не умеет читать этот язык.\n"
    "ПРАВИЛА:\n"
    "1. Сначала напиши естественный перевод фразы на {target_lang}.\n"
    "2. После перевода добавь в квадратных скобках [] подсказку произношения именно ПЕРЕВОДА.\n"
    "3. Подсказку произношения пиши буквами и фонетикой ИСХОДНОГО ЯЗЫКА, а не алфавитом языка перевода.\n"
    "4. Если исходный язык English, используй простую латиницу/английскую фонетику: "
    "Здравствуйте, как дела? [zdravstvuyte, kak dela?].\n"
    "5. Если исходный язык Russian, используй русские буквы: Hello, how are you? [хэллоу, хау ар ю?].\n"
    "6. Если исходный язык Spanish, French, German или другой, подбирай максимально понятную "
    "подсказку произношения для носителя исходного языка.\n"
    "7. Скобки НЕ должны быть транскрипцией исходной фразы. Скобки всегда помогают произнести ПЕРЕВОД.\n"
    "8. Не добавляй пояснения, варианты, кавычки, markdown и повтор исходного текста вне скобок.\n"
    "ФОРМАТ ОТВЕТА: Перевод на {target_lang} [как произнести этот перевод для носителя {source_lang}]"
)

AUTO_MIC_PROMPT = (
    "Ты переводишь живую речь стримера с иностранного языка на {target_lang} "
    "для OBS-субтитров.\n"
    "ПРАВИЛА:\n"
    "1. Переводи ТОЛЬКО целевую фразу, не пересказывай предыдущие фразы.\n"
    "2. Если фраза уже на языке {target_lang} или это мусор/мычание - ответь строго WAIT.\n"
    "3. Максимум 10 слов. Одна короткая строка. Без пояснений.\n"
    "4. Не добавляй информацию, которой нет в целевой фразе.\n"
    "Выдавай только чистый перевод на {target_lang}."
)

GAME_PROMPT = (
    "Ты переводишь живую игровую речь на {target_lang} для OBS-субтитров.\n"
    "ПРАВИЛА:\n"
    "1. Переводи ТОЛЬКО целевую фразу. Предыдущие фразы не повторяй и не пересказывай.\n"
    "2. Не склеивай новую фразу со старым смыслом, даже если тема похожа.\n"
    "3. Максимум 12 слов или 1 короткое предложение.\n"
    "4. Если фраза оборвана - переведи только понятную часть и поставь ...\n"
    "5. Если это бессмысленный огрызок в 1-2 слова - ответь строго WAIT.\n"
    "Выдавай только чистый субтитр на {target_lang}."
)

VIDEO_PROMPT = (
    "Ты переводишь видео, интервью или длинную живую речь на {target_lang}.\n"
    "ПРАВИЛА:\n"
    "1. Переводи ТОЛЬКО целевую фразу, не повторяй исходный текст.\n"
    "2. Переводи фразу ЦЕЛИКОМ. Не сокращай, не пересказывай и не выкидывай части смысла.\n"
    "3. Количество слов НЕ ОГРАНИЧЕНО. Длинную фразу можно переводить длинной фразой.\n"
    "4. Сохраняй естественную речь на языке {target_lang}, но не добавляй факты от себя.\n"
    "5. Не используй WAIT, если в целевой фразе есть понятный смысл.\n"
    "Выдавай только чистый перевод на {target_lang}."
)


def system_prompt_for_mode(
    *,
    is_voice_mode: bool = False,
    is_auto_mic: bool = False,
    is_video_mode: bool = False,
    target_lang: str = "Английский",
    source_lang: str = "Auto",
) -> str:
    if is_voice_mode:
        return VOICE_PROMPT_TEMPLATE.format(
            target_lang=target_lang,
            target_lang_upper=target_lang.upper(),
            source_lang=source_lang,
        )

    if is_auto_mic:
        return AUTO_MIC_PROMPT.format(target_lang=target_lang)

    if is_video_mode:
        return VIDEO_PROMPT.format(target_lang=target_lang)

    return GAME_PROMPT.format(target_lang=target_lang)


def build_prompt(
    *,
    target_text: str,
    force_translate_note: str = "",
    is_voice_mode: bool = False,
    is_auto_mic: bool = False,
    is_video_mode: bool = False,
    target_lang: str = "Английский",
    source_lang: str = "Auto",
) -> str:
    sys_prompt = system_prompt_for_mode(
        is_voice_mode=is_voice_mode,
        is_auto_mic=is_auto_mic,
        is_video_mode=is_video_mode,
        target_lang=target_lang,
        source_lang=source_lang,
    )
    clean_target = str(target_text or "").strip()

    return (
        f"{sys_prompt}\n\n"
        f"<ЦЕЛЕВАЯ_ФРАЗА>\n{clean_target}{force_translate_note}\n</ЦЕЛЕВАЯ_ФРАЗА>"
    )
