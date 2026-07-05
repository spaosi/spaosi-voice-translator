# Spaosi Voice Translator

[English version](README.en.md)

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

```bat
build_windows_exe.bat
```

Скрипт показывает прогресс сборки:

```text
[1/9] Searching for Python 3.10+
[2/9] Creating build virtual environment
[3/9] Activating build environment
[4/9] Upgrading pip
[5/9] Installing project dependencies
[6/9] Cleaning old build folders
[7/9] Preparing icon
[8/9] Building EXE with PyInstaller
[9/9] Checking final EXE
```

После сборки файл будет здесь:

```text
dist\Spaosi Voice Translator\Spaosi Voice Translator.exe
```

Передавать другим людям нужно всю папку:

```text
dist\Spaosi Voice Translator\
```

Не только `.exe`, потому что рядом лежат зависимости.

## Иконка приложения

Для кастомной иконки положи файл в корень проекта:

```text
icon.ico
```

Также поддерживается:

```text
icon.png
```

Если файл найден, сборщик добавит иконку в `.exe`.

## OBS

OBS Browser Source:

```text
http://127.0.0.1:8088/obs
```

Рекомендуемый размер источника:

```text
1920x1080
```

## Локальные настройки

Приложение создаёт файл:

```text
settings.local.json
```

Этот файл нельзя коммитить, потому что он может содержать:

- API-ключи;
- optional Gemini proxy URL;
- ID локальных аудиоустройств;
- позиции окон.

Безопасный пример настроек:

```text
settings.example.json
```

## Разработка

Установка зависимостей для разработки:

```bat
py -3 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .[dev]
```

Запуск тестов:

```bat
pytest -q
```

## Структура проекта

```text
src/spaosi_voice_translator/
├── app/
├── core/
├── services/
└── ui/

tests/
```
