# Spaosi Voice Translator

Десктопное приложение для перевода живой речи в реальном времени.

Приложение слушает системный звук или микрофон, распознаёт речь через Deepgram, переводит через Gemini API и показывает субтитры в оверлеях или OBS Browser Source.

## Возможности

- Перевод системного звука в реальном времени.
- Перевод микрофона по горячей клавише.
- Отдельный выбор языка распознавания и языка перевода.
- Подсказка произношения для перевода с микрофона.
- OBS widget для субтитров.
- Локальное хранение ключей и настроек в `settings.local.json`.
- Gemini proxy необязателен: можно оставить поле proxy пустым.

## Технологии

- Python
- PyQt6
- Deepgram
- Gemini API
- soundcard
- keyboard
- pytest
- PyInstaller

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

## Что можно удалить из GitHub-репозитория

Можно удалить:

```text
run_windows.bat
run_windows_hidden.vbs
```

`run_windows.bat` больше не нужен, если основной сценарий — сборка `.exe`.

Также не нужно коммитить:

```text
.venv/
.venv-build/
build/
dist/
logs/
__pycache__/
*.pyc
*.log
settings.local.json
settings.local.json.tmp
.env
.env.*
*.spec
```

Эти файлы уже должны быть в `.gitignore`.

## Разработка

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
