# Spaosi Voice Translator

[Русская версия](README.md)

A desktop application for real-time live speech translation.

The app listens to system audio or microphone input, transcribes speech with Deepgram, translates text with the Gemini API, and shows subtitles in desktop overlays or an OBS Browser Source.

## Features

- Real-time system audio translation.
- Microphone translation with a global hotkey.
- Separate recognition language and translation target language.
- Pronunciation guide for microphone translations.
- OBS subtitle widget.
- Local settings and API keys stored in `settings.local.json`.
- Direct Gemini API support or optional Gemini proxy.
- Windows `.exe` build through PyInstaller.

## Tech Stack

- Python
- PyQt6
- Deepgram
- Gemini API
- soundcard
- keyboard
- pytest
- PyInstaller

## Requirements

- Windows
- Python 3.10+
- Deepgram API key
- Gemini API key

## Build EXE

```bat
build_windows_exe.bat
```

The build script shows progress:

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

The final executable will be created here:

```text
dist\Spaosi Voice Translator\Spaosi Voice Translator.exe
```

Send or copy the whole folder:

```text
dist\Spaosi Voice Translator\
```

Do not send only the `.exe`, because the folder also contains required dependencies.

## Application Icon

For a custom icon, place this file in the project root:

```text
icon.ico
```

Also supported:

```text
icon.png
```

If the file exists, the build script will add it to the `.exe`.

## OBS

OBS Browser Source:

```text
http://127.0.0.1:8088/obs
```

Recommended source size:

```text
1920x1080
```

## Local Settings

The app creates this file:

```text
settings.local.json
```

Do not commit this file because it may contain:

- API keys;
- optional Gemini proxy URL;
- local audio device IDs;
- window positions.

A safe settings example is available here:

```text
settings.example.json
```

## Development

Install development dependencies:

```bat
py -3 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .[dev]
```

Run tests:

```bat
pytest -q
```

## Project Structure

```text
src/spaosi_voice_translator/
├── app/
├── core/
├── services/
└── ui/

tests/
```
