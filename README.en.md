# Spaosi Voice Translator

[Русская версия](README.md)

**A Windows desktop application for real-time live speech translation with system-audio capture, microphone hotkeys, streaming speech recognition, AI translation, desktop overlays, and OBS subtitles.**

**Stack:** Windows · Python 3.10+ · PyQt6 · Deepgram Nova-3 · Gemini API · WASAPI · OBS · pytest · PyInstaller

[Download Spaosi Voice Translator v0.1.1](https://github.com/spaosi/spaosi-voice-translator/releases/download/v0.1.1/Spaosi.Voice.Translator.v0.1.1.zip)

---

## About the Project

Spaosi Voice Translator is a desktop application designed to translate live speech with low latency.

It supports two independent workflows:

* **system audio translation** — for games, streams, calls, or videos;
* **microphone translation through a global hotkey** — press once to start recording and press again to finish the phrase and translate it.

The application captures audio, converts it into a PCM stream, sends speech to Deepgram over WebSocket, processes interim and final transcription results, segments phrases, translates them through the Gemini API, and displays the output:

* in desktop overlays;
* in a dedicated microphone overlay;
* in an OBS Browser Source through a built-in local HTTP server.

The project is structured as a modular desktop application rather than a single API wrapper script.

---

## Key Features

* Real-time system audio translation.
* Windows audio capture through WASAPI loopback.
* Microphone translation through a configurable global hotkey.
* Independent recognition and translation target languages.
* **88 configured recognition language/locale options** in the current application catalog.
* **30 translation target languages** in the current application catalog.
* Russian, English, Spanish, French, and German UI languages.
* Streaming transcription with Deepgram Nova-3.
* Interim and final STT results.
* Separate **Realtime** and **Video Translation** modes.
* Unicode-aware phrase segmentation.
* Dedicated handling for Japanese, Chinese, and other languages without regular word spacing.
* Duplicate and repeated phrase filtering.
* Translation through the Gemini API.
* Direct Gemini API access or an optional proxy endpoint.
* Background translation queue without blocking the UI.
* Desktop overlays for external speech and microphone translation.
* Built-in OBS Browser Source.
* Pronunciation guidance for microphone translations.
* Selectable audio output and microphone devices.
* Persistent window geometry.
* Local settings persistence.
* Automatic Deepgram reconnection after WebSocket loss.
* Recovery from broken SSL certificate paths in Windows environments.
* Windows application packaging through PyInstaller.
* Automated tests with pytest.

---

## Processing Pipeline

```text
┌─────────────────────┐
│   System Audio      │
│   WASAPI Loopback   │
└──────────┬──────────┘
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

The microphone workflow uses a separate runtime flow:

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

## Engineering Details

### Modular Architecture

The source code is separated by responsibility:

* `app/` — bootstrap, application context, and window coordination;
* `core/` — settings, i18n, logging, signals, and constants;
* `services/audio/` — system audio and microphone capture;
* `services/speech/` — Deepgram WebSocket engine;
* `services/pipeline/` — orchestration and phrase segmentation;
* `services/translation/` — Gemini translation pipeline and prompts;
* `services/obs/` — local HTTP server for OBS;
* `services/hotkeys/` — global hotkey handling;
* `ui/` — windows, settings, layouts, widgets, and theme.

This separation allows the STT layer, translation service, UI, or OBS integration to evolve without moving the entire application into one main file.

---

### Non-Blocking Processing

Long-running operations are kept outside the main GUI thread:

* system audio capture runs in a dedicated `QThread`;
* microphone capture runs in a dedicated `QThread`;
* Gemini translation uses its own worker thread;
* Deepgram connection, audio sender, and reconnect logic run in background threads;
* OBS is served by a separate `ThreadingHTTPServer`.

The PyQt interface communicates with services through signals and slots.

---

### Resilient Deepgram WebSocket Handling

The Deepgram engine implements:

* live WebSocket transcription;
* interim results;
* final results;
* configurable endpointing;
* an audio packet queue;
* keepalive behavior;
* connection close handling;
* automatic reconnection;
* a bounded number of reconnect attempts;
* increasing delay between reconnect attempts;
* queue cleanup on shutdown;
* suppression of duplicated low-level third-party WebSocket log noise.

The Windows runtime also handles broken paths in:

* `SSL_CERT_FILE`;
* `REQUESTS_CA_BUNDLE`;
* `CURL_CA_BUNDLE`.

When the environment points to a deleted certificate bundle, the application removes invalid values and uses an available `certifi` bundle.

---

### Unicode-Aware Phrase Segmentation

`RealtimePhraseSegmenter` is not restricted to ASCII or Cyrillic text.

The implementation includes:

* Unicode-aware word extraction;
* NFKC Unicode normalization;
* `casefold()` normalization;
* deduplication of previously emitted segments;
* word-overlap checks;
* splitting of oversized real-time phrases;
* punctuation-boundary detection;
* compact-script handling.

Dedicated handling includes:

* Hiragana;
* Katakana;
* CJK ideographs;
* Hangul.

This prevents Japanese and Chinese phrases from being discarded simply because they do not contain standard spaces between words.

Example of a correctly handled phrase:

```text
嫌いな国とかってどこかあったりします？
```

---

### Background Gemini Translation Queue

Translation runs independently from the UI thread.

The implementation includes:

* a bounded translation queue;
* a dedicated worker thread;
* reusable `requests.Session`;
* HTTP timeouts;
* HTTP error handling;
* extraction of API error details;
* pending-job cancellation;
* generation-based invalidation of stale tasks;
* repeated-output filtering;
* mode-specific prompts.

Supported connection modes:

* direct Gemini API;
* optional Gemini proxy endpoint.

The current implementation is configured with:

```text
gemini-3.1-flash-lite
```

---

### Built-In OBS Integration

The application starts a local HTTP server at:

```text
http://127.0.0.1:8088/obs
```

Available endpoints:

```text
/obs
/api/text
```

The OBS widget:

* requires no separate Node.js, PHP, or external backend server;
* runs locally;
* retrieves subtitle updates over HTTP;
* supports both external speech and microphone output;
* visually distinguishes message types;
* keeps a short subtitle history;
* automatically hides stale text;
* removes duplicates;
* filters repeated sentences;
* normalizes punctuation;
* uses `Cache-Control: no-store`.

Recommended OBS Browser Source size:

```text
1920 × 1080
```

---

### Local Settings Persistence

Settings are stored in:

```text
settings.local.json
```

Persisted values include:

* Deepgram API key;
* Gemini API key;
* Gemini proxy URL;
* UI language;
* recognition language;
* translation target language;
* global hotkey;
* selected system audio device;
* selected microphone;
* endpointing pauses;
* Video Translation mode;
* OBS URL;
* window positions and sizes.

Settings are written through a temporary file followed by replacement of the target file:

```text
settings.local.json.tmp
        ↓
settings.local.json
```

`settings.local.json` is excluded from Git through `.gitignore`.

---

## Translation Modes

| Mode                  | Intended Use                         | Behavior                                                                                         |
| --------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------ |
| **Realtime**          | Games, streams, calls, live speech   | Fast segmentation, up to 14 words per real-time phrase, optional early processing of interim STT |
| **Video Translation** | Videos, interviews, long-form speech | Fixed 600 ms SYS pause, no phrase word limit, no OBS text trimming                               |
| **Microphone**        | Translating the user's own speech    | Hotkey-controlled start/stop recording, separate STT flow, translation after phrase completion   |

---

## Pronunciation Guidance

For microphone translations, the application can return:

1. the translation;
2. a guide for pronouncing the translated phrase.

Example source phrase:

```text
Hello, how are you?
```

Translated into Russian for an English-speaking user:

```text
Здравствуйте, как дела? [zdravstvuyte, kak dela?]
```

A Russian phrase translated into English for a Russian-speaking user:

```text
Hello, how are you? [хэллоу, хау ар ю?]
```

The pronunciation guide is generated with the source-language speaker in mind.

For clean OBS subtitles, the pronunciation guide is removed before display.

---

## Languages

### Interface Languages

* Русский
* English
* Español
* Français
* Deutsch

All declared UI languages use the same translation-key set with fallback behavior.

Technical service logs are also normalized between Russian and English representations.

### Speech Recognition

The current application catalog contains **88 configured language and locale options**, including:

* English;
* Russian;
* Ukrainian;
* Japanese;
* Korean;
* Chinese;
* Arabic and regional variants;
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
* and others.

### Translation Targets

The current catalog contains **30 target languages**.

Recognition and translation target languages are selected independently.

---

## Technology Stack

| Component            | Technology                   |
| -------------------- | ---------------------------- |
| Language             | Python 3.10+                 |
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

## Requirements

* Windows with an available audio stack;
* Python 3.10 or newer;
* Deepgram API key;
* Gemini API key;
* internet access for cloud STT and translation;
* OBS Studio only when OBS subtitles are required.

---

## Quick Start from Source

### 1. Clone the repository

```powershell
git clone https://github.com/spaosi/spaosi-voice-translator.git
cd spaosi-voice-translator
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

### 5. Run the application

```powershell
python main.py
```

API keys can be configured through the application settings after startup.

---

## OBS Setup

1. Start Spaosi Voice Translator.
2. Open OBS Studio.
3. Add a new **Browser Source**.
4. Set the URL to:

```text
http://127.0.0.1:8088/obs
```

5. Set the source size:

```text
Width:  1920
Height: 1080
```

The OBS URL is also available in the application settings and can be copied with a click.

---

## Building the Windows EXE

The repository contains:

```text
build_windows_exe.bat
```

Run:

```bat
build_windows_exe.bat
```

The build script automatically:

1. searches for Python 3.10+;
2. creates a dedicated `.venv-build`;
3. upgrades pip;
4. installs project dependencies;
5. verifies Deepgram SDK compatibility;
6. stops old application processes from the build directory;
7. cleans previous `build/` and `dist/` directories;
8. detects `icon.ico` or `icon.png`;
9. builds a windowed application with PyInstaller;
10. verifies that the final `.exe` exists.

Output:

```text
dist\
└── Spaosi Voice Translator\
    └── Spaosi Voice Translator.exe
```

Distribute the entire directory:

```text
dist\Spaosi Voice Translator\
```

not only the standalone `.exe` file.

---

## Tests

Install development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run the test suite:

```powershell
python -m pytest
```

Run lint checks:

```powershell
python -m ruff check .
```

The current project contains **24 pytest test cases** across 6 test modules.

The tests cover, among other areas:

* settings persistence;
* UI localization;
* consistent translation-key sets;
* service log localization;
* Deepgram SSL environment recovery;
* Gemini direct API URL/header behavior;
* Gemini proxy compatibility;
* Unicode phrase segmentation;
* Japanese phrases;
* Chinese phrases;
* CJK text deduplication;
* preservation of existing English segmenter behavior;
* microphone pronunciation prompts;
* removal of pronunciation guidance before OBS output.

---

## Project Structure

```text
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
│       │   ├── i18n.py
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
```

---

## What the Project Demonstrates

From an engineering perspective, Spaosi Voice Translator includes several problems commonly found in real desktop software:

* real-time audio processing;
* Windows audio capture;
* streaming WebSocket integration;
* asynchronous and background processing;
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

## Limitations

* The current system-audio capture implementation is Windows-oriented.
* Speech recognition and translation depend on external cloud APIs.
* The OBS Browser Source is available only while the application is running.
* Output quality depends on input audio quality, selected recognition language, and external model behavior.

---

## License

This project is distributed under the **MIT License**.

See [`LICENSE`](LICENSE) for details.
