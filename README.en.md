# Spaosi Voice Translator

[Русская версия](README.md)

## Download for Windows

[Download Spaosi Voice Translator v0.1.1](https://github.com/spaosi/spaosi-voice-translator/releases/download/v0.1.1/Spaosi.Voice.Translator.v0.1.1.zip)

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
