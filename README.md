# Spaosi Voice Translator

[English version](README.en.md)

## Скачать для Windows

[Download Spaosi Voice Translator v0.1.1](https://github.com/spaosi/spaosi-voice-translator/releases/download/v0.1.1/Spaosi.Voice.Translator.v0.1.1.zip)

Десктопное приложение для перевода живой речи в реальном времени.

Приложение слушает системный звук или микрофон, распознаёт речь через Deepgram, переводит через Gemini API и показывает субтитры в оверлеях или OBS Browser Source.

## Возможности

- Перевод системного звука в реальном времени.
- Перевод микрофона по горячей клавише.
- Отдельный выбор языка распознавания и языка перевода.
- Подсказка произношения для перевода с микрофона.
- OBS widget для субтитров.
- Локальное хранение ключей и настроек в `settings.local.json`.
- Работа с Gemini API напрямую или через optional proxy.
- Сборка Windows `.exe` через PyInstaller.

## Технологии

- Python
- PyQt6
- Deepgram
- Gemini API
- soundcard
- keyboard
- pytest
- PyInstaller

## Требования

- Windows
- Python 3.10+
- Deepgram API key
- Gemini API key

## Сборка EXE
