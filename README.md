# Spaosi Voice Translator

[English version](README.en.md)

**Десктопное Windows-приложение для перевода живой речи в реальном времени: системный звук, микрофон, потоковое распознавание речи, AI-перевод, экранные оверлеи и субтитры для OBS.**

**Стек:** Windows · Python 3.10+ · PyQt6 · Deepgram Nova-3 · Gemini API · WASAPI · OBS · pytest · PyInstaller

[Скачать Spaosi Voice Translator v0.1.1](https://github.com/spaosi/spaosi-voice-translator/releases/download/v0.1.1/Spaosi.Voice.Translator.v0.1.1.zip)

---

## О проекте

Spaosi Voice Translator — приложение для перевода живой речи с минимальной задержкой.

Оно поддерживает два независимых сценария:

* **перевод системного звука** — например, игры, стрима, звонка или видео;
* **перевод микрофона по глобальной горячей клавише** — нажать один раз для начала записи и ещё раз для завершения фразы и перевода.

Приложение захватывает аудио, преобразует его в поток PCM, отправляет речь в Deepgram через WebSocket, обрабатывает промежуточные и финальные результаты, сегментирует фразы, переводит их через Gemini API и отображает результат:

* в desktop overlays;
* в отдельном оверлее микрофона;
* в OBS Browser Source через встроенный локальный HTTP-сервер.

Проект построен как модульное desktop-приложение, а не как единый скрипт вокруг API.

---

## Основные возможности

* Перевод системного звука в реальном времени.
* Захват Windows-аудио через WASAPI loopback.
* Перевод микрофона по настраиваемой глобальной горячей клавише.
* Независимый выбор языка распознавания и языка перевода.
* **88 настроенных вариантов языка/локали распознавания** в текущем каталоге приложения.
* **30 языков перевода** в текущем каталоге приложения.
* Интерфейс на русском, английском, испанском, французском и немецком языках.
* Потоковое распознавание через Deepgram Nova-3.
* Промежуточные и финальные STT-результаты.
* Отдельные режимы **Realtime** и **Video Translation**.
* Unicode-aware сегментация текста.
* Отдельная обработка японского, китайского и других языков без пробелов между словами.
* Фильтрация повторяющихся фраз и дублей.
* Перевод через Gemini API.
* Работа с Gemini API напрямую или через необязательный proxy endpoint.
* Фоновая очередь переводов без блокировки интерфейса.
* Desktop overlays для внешней речи и микрофона.
* Встроенный OBS Browser Source.
* Подсказка произношения для перевода с микрофона.
* Выбор аудиоустройства и микрофона.
* Сохранение расположения и размеров окон.
* Локальное сохранение настроек.
* Автоматическое переподключение к Deepgram после потери WebSocket.
* Восстановление после некорректных SSL certificate paths в Windows-окружении.
* Сборка Windows-приложения через PyInstaller.
* Автоматизированные тесты через pytest.

---

## Как работает pipeline

```text
┌─────────────────────┐
│   System Audio      │
│   WASAPI Loopback   │
└──────────┬──────────┘
           │
           │
           ▼
┌─────────────────────┐
│  Audio Capture      │
│  PyQt QThread       │
│  soundcard + NumPy  │
└──────────┬──────────┘
           │
           │ 16 kHz / mono / PCM16
           ▼
┌─────────────────────┐
│ Deepgram Nova-3     │
│ Live WebSocket STT  │
│ interim + final     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Realtime Phrase     │
│ Segmenter           │
│ Unicode + dedupe    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Gemini Translator   │
│ Background Queue    │
│ Worker Thread       │
└──────────┬──────────┘
           │
     ┌─────┴───────────────┐
     ▼                     ▼
┌──────────────┐   ┌──────────────────┐
│ PyQt Overlay │   │ Local OBS Server │
│ Desktop UI   │   │ /obs + /api/text │
└──────────────┘   └──────────────────┘
```

Для микрофона используется отдельный runtime flow:

```text
Global Hotkey
     │
     ▼
Start Recording
     │
     ▼
Microphone QThread
     │
     ▼
Deepgram Live STT
     │
     ▼
Accumulate Final Text
     │
     ▼
Second Hotkey Press
     │
     ▼
Gemini Translation
     │
     ├── Desktop Voice Overlay
     └── OBS Subtitle
```

---

## Инженерные детали

### Модульная архитектура

Код разделён по ответственности:

* `app/` — bootstrap, application context, управление окнами;
* `core/` — настройки, i18n, логирование, сигналы, константы;
* `services/audio/` — захват системного звука и микрофона;
* `services/speech/` — Deepgram WebSocket engine;
* `services/pipeline/` — orchestration и сегментация фраз;
* `services/translation/` — Gemini translation pipeline и prompts;
* `services/obs/` — локальный HTTP server для OBS;
* `services/hotkeys/` — глобальные горячие клавиши;
* `ui/` — окна, настройки, layout, widgets и тема.

Такое разделение позволяет изменять STT, переводчик, UI или OBS-интеграцию без переноса всей логики в один главный файл.

---

### Неблокирующая обработка

Долгие операции вынесены из основного GUI thread:

* системный звук захватывается в отдельном `QThread`;
* микрофон работает в отдельном `QThread`;
* Gemini использует собственный worker thread;
* Deepgram connection, audio sender и reconnect работают в фоновых потоках;
* OBS обслуживается отдельным `ThreadingHTTPServer`.

PyQt-интерфейс взаимодействует с сервисами через signals/slots.

---

### Устойчивое Deepgram WebSocket-соединение

Deepgram engine реализует:

* live WebSocket transcription;
* промежуточные результаты;
* финальные результаты;
* configurable endpointing;
* очередь аудиопакетов;
* keepalive;
* обработку закрытия соединения;
* автоматический reconnect;
* ограниченное количество повторных попыток;
* увеличиваемую задержку между reconnect-попытками;
* очистку очереди при остановке;
* подавление дублирующего технического шума сторонних WebSocket-логгеров.

Для Windows дополнительно обрабатываются сломанные пути:

* `SSL_CERT_FILE`;
* `REQUESTS_CA_BUNDLE`;
* `CURL_CA_BUNDLE`.

Если окружение ссылается на удалённый certificate bundle, приложение удаляет некорректные значения и использует доступный `certifi` bundle.

---

### Unicode-aware сегментация речи

`RealtimePhraseSegmenter` не ограничен ASCII или кириллицей.

Реализованы:

* Unicode word extraction;
* Unicode normalization через NFKC;
* `casefold()` для нормализации регистра;
* дедупликация уже обработанных сегментов;
* проверка пересечения слов;
* разбиение длинных realtime-фраз;
* обработка punctuation boundaries;
* поддержка compact scripts.

Отдельно учитываются:

* Hiragana;
* Katakana;
* CJK ideographs;
* Hangul.

Это позволяет не отбрасывать японские и китайские фразы только потому, что в них нет обычных пробелов между словами.

Пример корректно обрабатываемой фразы:

```text
嫌いな国とかってどこかあったりします？
```

---

### Фоновая очередь Gemini

Переводчик работает независимо от UI thread.

Реализованы:

* bounded translation queue;
* отдельный worker thread;
* повторное использование `requests.Session`;
* таймауты HTTP-запросов;
* обработка HTTP errors;
* извлечение деталей API error response;
* очистка pending jobs;
* generation-based invalidation устаревших задач;
* фильтрация повторяющихся результатов;
* отдельные prompts для разных режимов.

Поддерживаются:

* прямой Gemini API;
* необязательный Gemini proxy endpoint.

В текущей реализации используется модель:

```text
gemini-3.1-flash-lite
```

---

### Встроенная OBS-интеграция

Приложение запускает локальный HTTP server:

```text
http://127.0.0.1:8088/obs
```

Доступные endpoints:

```text
/obs
/api/text
```

OBS widget:

* не требует отдельного Node.js/PHP/backend-сервера;
* работает локально;
* получает новые субтитры через HTTP;
* поддерживает внешнюю речь и микрофон;
* визуально разделяет типы сообщений;
* хранит короткую историю последних субтитров;
* автоматически скрывает устаревший текст;
* удаляет повторы;
* фильтрует повторяющиеся предложения;
* нормализует пунктуацию;
* использует `Cache-Control: no-store`.

Рекомендуемый размер OBS Browser Source:

```text
1920 × 1080
```

---

### Локальные настройки

Настройки сохраняются в:

```text
settings.local.json
```

Сохраняются, в частности:

* Deepgram API key;
* Gemini API key;
* Gemini proxy URL;
* язык интерфейса;
* язык распознавания;
* язык перевода;
* глобальный hotkey;
* выбранное устройство системного звука;
* выбранный микрофон;
* endpointing pauses;
* режим Video Translation;
* OBS URL;
* положение и размер окон.

Запись выполняется через временный файл с последующей заменой целевого файла:

```text
settings.local.json.tmp
        ↓
settings.local.json
```

`settings.local.json` исключён из Git через `.gitignore`.

---

## Режимы перевода

| Режим                 | Назначение                       | Поведение                                                                                |
| --------------------- | -------------------------------- | ---------------------------------------------------------------------------------------- |
| **Realtime**          | Игры, стримы, звонки, живая речь | Быстрая сегментация, до 14 слов на realtime-фразу, возможна ранняя обработка interim STT |
| **Video Translation** | Видео, интервью, длинные фразы   | Фиксированная пауза SYS 600 мс, без лимита фразы по словам, без обрезки OBS-текста       |
| **Microphone**        | Перевод собственной речи         | Hotkey для начала/остановки записи, отдельный STT flow, перевод после завершения фразы   |

---

## Подсказка произношения

Для микрофона приложение может возвращать:

1. перевод;
2. подсказку, как произнести именно перевод.

Пример:

```text
Hello, how are you?
```

При переводе на русский для англоязычного пользователя:

```text
Здравствуйте, как дела? [zdravstvuyte, kak dela?]
```

При переводе русского текста на английский для русскоязычного пользователя:

```text
Hello, how are you? [хэллоу, хау ар ю?]
```

Подсказка строится с учётом исходного языка пользователя.

Для чистых OBS-субтитров pronunciation guide удаляется перед показом текста.

---

## Языки

### Языки интерфейса

* Русский
* English
* Español
* Français
* Deutsch

Все объявленные UI languages используют единый набор translation keys с fallback-механизмом.

Технические service logs также локализуются между русским и английским представлением.

### Распознавание речи

Текущий каталог приложения содержит **88 вариантов языка и локали**, включая:

* English;
* Russian;
* Ukrainian;
* Japanese;
* Korean;
* Chinese;
* Arabic и региональные варианты;
* German;
* French;
* Spanish;
* Portuguese;
* Polish;
* Latvian;
* Lithuanian;
* Hindi;
* Thai;
* Vietnamese;
* и другие.

### Языки перевода

Текущий каталог содержит **30 target languages**.

Язык распознавания и язык перевода выбираются независимо.

---

## Технологии

| Компонент            | Технология                   |
| -------------------- | ---------------------------- |
| Язык                 | Python 3.10+                 |
| Desktop UI           | PyQt6                        |
| Audio capture        | soundcard                    |
| Windows system audio | WASAPI loopback              |
| Audio processing     | NumPy                        |
| Speech-to-Text       | Deepgram SDK                 |
| STT model            | Deepgram Nova-3              |
| Translation          | Gemini API                   |
| HTTP client          | requests                     |
| Global hotkeys       | keyboard                     |
| OBS integration      | Python `ThreadingHTTPServer` |
| Testing              | pytest                       |
| Linting              | Ruff                         |
| Windows packaging    | PyInstaller                  |
| Packaging metadata   | `pyproject.toml`             |

---

## Требования

* Windows с доступным audio stack;
* Python 3.10 или новее;
* Deepgram API key;
* Gemini API key;
* интернет-соединение для cloud STT и перевода;
* OBS Studio — только если нужны OBS-субтитры.

---

## Быстрый запуск из исходников

### 1. Клонировать репозиторий

```powershell
git clone https://github.com/spaosi/spaosi-voice-translator.git
cd spaosi-voice-translator
```

### 2. Создать virtual environment

```powershell
python -m venv .venv
```

### 3. Активировать окружение

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 4. Установить зависимости

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

### 5. Запустить приложение

```powershell
python main.py
```

После запуска API keys можно указать в настройках приложения.

---

## Настройка OBS

1. Запустите Spaosi Voice Translator.
2. Откройте OBS Studio.
3. Добавьте новый **Browser Source**.
4. Укажите URL:

```text
http://127.0.0.1:8088/obs
```

5. Установите размер:

```text
Width:  1920
Height: 1080
```

OBS URL также отображается в настройках приложения и может быть скопирован кликом.

---

## Сборка Windows EXE

В репозитории находится:

```text
build_windows_exe.bat
```

Запуск:

```bat
build_windows_exe.bat
```

Build script автоматически:

1. ищет Python 3.10+;
2. создаёт отдельное `.venv-build`;
3. обновляет pip;
4. устанавливает зависимости проекта;
5. проверяет совместимость Deepgram SDK;
6. завершает старые процессы приложения из build directory;
7. очищает старые `build/` и `dist/`;
8. ищет `icon.ico` или `icon.png`;
9. собирает windowed-приложение через PyInstaller;
10. проверяет наличие итогового `.exe`.

Результат:

```text
dist\
└── Spaosi Voice Translator\
    └── Spaosi Voice Translator.exe
```

Для распространения необходимо передавать всю папку:

```text
dist\Spaosi Voice Translator\
```

а не только отдельный `.exe`.

---

## Тесты

Установить dev dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Запустить тесты:

```powershell
python -m pytest
```

Проверить lint:

```powershell
python -m ruff check .
```

В текущем проекте находится **24 pytest test cases** в 6 test modules.

Проверяются, в частности:

* сохранение и загрузка settings;
* UI localization;
* одинаковый набор translation keys;
* локализация service logs;
* Deepgram SSL environment recovery;
* Gemini direct API URL/header behavior;
* Gemini proxy compatibility;
* Unicode phrase segmentation;
* японские фразы;
* китайские фразы;
* дедупликация CJK-текста;
* сохранение английского поведения segmenter;
* microphone pronunciation prompts;
* удаление pronunciation guide перед OBS output.

---

## Структура проекта

````text
.
├── src/
│   └── spaosi_voice_translator/
│       ├── app/
│       │   ├── app_context.py
│       │   ├── bootstrap.py
│       │   └── window_manager.py
│       │
│       ├── core/
│       │   ├── app_icon.py
│       │   ├── constants.py
│       │ перед OBS output.

---

## Структура проекта

```text
.
├── src/
│   └── spaosi_voice_translator/
│       ├── app/
│       │   ├── app_context.py
│       │   ├── bootstrap.py
│       │   └   ├── i18n.py
│       │   ├── log_localizer.py
│       │   ├── logger.py
│       │   ├── settings.py
│       │   └── signals.py
│       │
│       ├── services/
│       │   ├── audio/
│       │   ├── hotkeys/
│       │   ├── obs/
│       │   ├── pipeline/
│       │   ├── speech/
│       │   └── translation/
│       │
│       └── ui/
│           ├── layout/
│           ├── settings/
│           ├── theme/
│           ├── widgets/
│           └── windows/
│
├── tests/
├── build_windows_exe.bat
├── main.py
├── pyproject.toml
├── settings.example.json
├── README.md
├── README.en.md
└── LICENSE
````

---

## Что демонстрирует проект с инженерной стороны

Spaosi Voice Translator включает несколько задач, характерных для реального desktop software:

* real-time audio processing;
* Windows audio capture;
* streaming WebSocket integration;
* asynchronous/background processing;
* bounded queues;
* reconnect and failure recovery;
* Unicode text processing;
* multilingual UI;
* third-party API integration;
* local HTTP integration;
* state persistence;
* modular application architecture;
* desktop packaging;
* automated testing.

---

## Ограничения

* Реализация захвата системного звука ориентирована на Windows.
* Распознавание и перевод зависят от внешних cloud API.
* OBS Browser Source доступен только во время работы приложения.
* Качество результата зависит от качества входного аудио, выбранного языка распознавания и поведения внешних моделей.

---

## Лицензия

Проект распространяется по лицензии **MIT**.

Подробности находятся в файле [`LICENSE`](LICENSE).
